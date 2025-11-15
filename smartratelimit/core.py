"""Core RateLimiter class."""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Optional
from urllib.parse import urlparse

import requests

from smartratelimit.detector import RateLimitDetector
from smartratelimit.models import RateLimit, RateLimitStatus, TokenBucket
from smartratelimit.storage import (
    MemoryStorage,
    RedisStorage,
    SQLiteStorage,
    StorageBackend,
)

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded and raise_on_limit=True."""

    pass


class RateLimiter:
    """
    Main rate limiter class that automatically manages API rate limits.

    Example:
        >>> limiter = RateLimiter()
        >>> response = limiter.request('GET', 'https://api.github.com/users')
        >>> print(response.status_code)
        200
    """

    def __init__(
        self,
        storage: str = "memory",
        default_limits: Optional[Dict[str, int]] = None,
        headers_map: Optional[Dict[str, str]] = None,
        raise_on_limit: bool = False,
    ):
        """
        Initialize rate limiter.

        Args:
            storage: Storage backend ('memory', 'sqlite:///path', 'redis://host:port')
            default_limits: Default limits like {'requests_per_second': 10}
            headers_map: Custom header name mapping
            raise_on_limit: If True, raise exception instead of waiting
        """
        self._storage = self._create_storage(storage)
        self._detector = RateLimitDetector(headers_map)
        self._default_limits = default_limits or {}
        self._raise_on_limit = raise_on_limit
        self._session = requests.Session()

    def _create_storage(self, storage: str) -> StorageBackend:
        """Create storage backend from string specification."""
        if storage == "memory":
            return MemoryStorage()

        if storage.startswith("sqlite://"):
            db_path = storage.replace("sqlite://", "", 1)
            # Handle different sqlite:// formats
            if db_path.startswith("///"):
                # sqlite:///absolute/path -> /absolute/path
                db_path = db_path[2:]
            elif db_path.startswith("//"):
                # sqlite:////absolute/path (4 slashes) -> /absolute/path
                db_path = db_path[1:]
            elif db_path == "/:memory:":
                # sqlite:///:memory: -> :memory:
                db_path = ":memory:"
            elif db_path.startswith("/"):
                # sqlite:///relative/path -> /relative/path (keep as is)
                pass
            elif not db_path:
                # sqlite:// -> :memory:
                db_path = ":memory:"
            try:
                return SQLiteStorage(db_path=db_path)
            except Exception as e:
                logger.warning(
                    f"Failed to initialize SQLite storage: {e}, falling back to memory"
                )
                return MemoryStorage()

        if storage.startswith("redis://"):
            try:
                return RedisStorage(redis_url=storage)
            except ImportError as e:
                logger.warning(
                    f"Redis package not installed: {e}, falling back to memory"
                )
                return MemoryStorage()
            except Exception as e:
                logger.warning(
                    f"Failed to initialize Redis storage: {e}, falling back to memory"
                )
                return MemoryStorage()

        raise ValueError(f"Unknown storage backend: {storage}")

    @staticmethod
    def _get_endpoint_key(url: str) -> str:
        """Extract endpoint key from URL."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _get_bucket_key(self, url: str, limit_type: str = "default") -> str:
        """Get token bucket key for URL."""
        endpoint = self._get_endpoint_key(url)
        return f"{endpoint}:{limit_type}"

    def _get_or_create_bucket(
        self, url: str, limit: int, window: timedelta
    ) -> TokenBucket:
        """Get or create token bucket for URL."""
        key = self._get_bucket_key(url)
        bucket = self._storage.get_token_bucket(key)

        if bucket is None:
            # Create new bucket
            capacity = float(limit)
            refill_rate = capacity / window.total_seconds()
            bucket = TokenBucket(
                capacity=capacity,
                tokens=capacity,
                refill_rate=refill_rate,
            )
            self._storage.set_token_bucket(key, bucket)
        else:
            # Update refill rate if limit changed
            window_seconds = window.total_seconds()
            if window_seconds > 0:
                bucket.refill_rate = float(limit) / window_seconds
                bucket.capacity = float(limit)

        return bucket

    def _wait_for_token(self, bucket: TokenBucket, url: str) -> None:
        """Wait until token is available."""
        wait_time = bucket.wait_time()
        if wait_time > 0:
            if self._raise_on_limit:
                raise RateLimitExceeded(
                    f"Rate limit exceeded for {url}. Wait {wait_time:.2f} seconds."
                )

            logger.info(
                f"Rate limit reached for {url}, waiting {wait_time:.2f} seconds"
            )
            time.sleep(wait_time)

        # Consume token
        bucket.refill()
        if not bucket.consume():
            # Should not happen after wait, but handle edge case
            time.sleep(0.1)
            bucket.refill()
            bucket.consume()

    def _update_from_response(self, response: requests.Response) -> None:
        """Update rate limit info from response headers."""
        detected = self._detector.detect_from_response(response)
        if not detected:
            return

        endpoint = self._get_endpoint_key(response.url)
        limit = detected.get("limit")
        remaining = detected.get("remaining")
        reset_time = detected.get("reset_time")
        window = detected.get("window")

        if limit and reset_time and window:
            rate_limit = RateLimit(
                endpoint=endpoint,
                limit=limit,
                remaining=remaining or limit,
                reset_time=reset_time,
                window=window,
            )
            self._storage.set_rate_limit(endpoint, rate_limit)

            # Update or create token bucket
            bucket = self._get_or_create_bucket(endpoint, limit, window)
            # Adjust tokens based on remaining
            if remaining is not None:
                bucket.tokens = min(bucket.capacity, float(remaining))
                bucket.last_update = datetime.utcnow()

            logger.debug(
                f"Rate limit updated for {endpoint}: {remaining}/{limit} remaining"
            )

    def _apply_default_limits(self, url: str) -> None:
        """Apply default limits if no rate limit info exists."""
        if not self._default_limits:
            return

        endpoint = self._get_endpoint_key(url)

        # Check if we already have rate limit info
        if self._storage.get_rate_limit(endpoint):
            return

        # Apply defaults
        if "requests_per_second" in self._default_limits:
            limit = self._default_limits["requests_per_second"]
            window = timedelta(seconds=1)
        elif "requests_per_minute" in self._default_limits:
            limit = self._default_limits["requests_per_minute"]
            window = timedelta(minutes=1)
        elif "requests_per_hour" in self._default_limits:
            limit = self._default_limits["requests_per_hour"]
            window = timedelta(hours=1)
        else:
            return

        # Create default rate limit
        rate_limit = RateLimit(
            endpoint=endpoint,
            limit=limit,
            remaining=limit,
            reset_time=datetime.utcnow() + window,
            window=window,
        )
        self._storage.set_rate_limit(endpoint, rate_limit)

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Make a rate-limited HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            url: Request URL
            **kwargs: Additional arguments passed to requests.request()

        Returns:
            requests.Response object

        Raises:
            RateLimitExceeded: If raise_on_limit=True and limit is exceeded
        """
        endpoint = self._get_endpoint_key(url)

        # Apply default limits if configured
        self._apply_default_limits(url)

        # Get rate limit info
        rate_limit = self._storage.get_rate_limit(endpoint)

        if rate_limit:
            # Use detected rate limits
            bucket = self._get_or_create_bucket(
                endpoint, rate_limit.limit, rate_limit.window
            )
            self._wait_for_token(bucket, url)
        elif self._default_limits:
            # Use default limits
            self._apply_default_limits(url)
            rate_limit = self._storage.get_rate_limit(endpoint)
            if rate_limit:
                bucket = self._get_or_create_bucket(
                    endpoint, rate_limit.limit, rate_limit.window
                )
                self._wait_for_token(bucket, url)

        # Make the request
        response = self._session.request(method, url, **kwargs)

        # Update rate limit info from response
        self._update_from_response(response)

        # Handle 429 responses
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    wait_time = int(retry_after)
                    logger.warning(
                        f"Received 429 for {url}, waiting {wait_time} seconds"
                    )
                    if not self._raise_on_limit:
                        time.sleep(wait_time)
                        # Retry once
                        response = self._session.request(method, url, **kwargs)
                        self._update_from_response(response)
                except (ValueError, TypeError):
                    pass

        # Save bucket state
        if rate_limit:
            bucket = self._get_or_create_bucket(
                endpoint, rate_limit.limit, rate_limit.window
            )
            self._storage.set_token_bucket(self._get_bucket_key(endpoint), bucket)

        return response

    def wrap_session(self, session: requests.Session) -> None:
        """
        Wrap an existing requests.Session with rate limiting.

        This modifies the session object in-place by wrapping its request method.

        Args:
            session: requests.Session object to wrap
        """
        original_request = session.request

        def rate_limited_request(method, url, **kwargs):
            return self.request(method, url, **kwargs)

        session.request = rate_limited_request

    def get_status(self, endpoint: str) -> Optional[RateLimitStatus]:
        """
        Get current rate limit status for an endpoint.

        Args:
            endpoint: Endpoint URL or domain

        Returns:
            RateLimitStatus object or None if no info available
        """
        # Normalize endpoint
        if not endpoint.startswith(("http://", "https://")):
            endpoint = f"https://{endpoint}"

        endpoint_key = self._get_endpoint_key(endpoint)
        rate_limit = self._storage.get_rate_limit(endpoint_key)

        if rate_limit:
            return rate_limit.to_status()

        return None

    def set_limit(
        self, endpoint: str, limit: int, window: str = "1h"
    ) -> None:
        """
        Manually set rate limit for an endpoint.

        Args:
            endpoint: Endpoint URL or domain
            limit: Maximum number of requests
            window: Time window (e.g., '1h', '1m', '30s', '1d')
        """
        # Normalize endpoint
        if not endpoint.startswith(("http://", "https://")):
            endpoint = f"https://{endpoint}"

        endpoint_key = self._get_endpoint_key(endpoint)

        # Parse window
        window_td = self._parse_window(window)

        rate_limit = RateLimit(
            endpoint=endpoint_key,
            limit=limit,
            remaining=limit,
            reset_time=datetime.utcnow() + window_td,
            window=window_td,
        )

        self._storage.set_rate_limit(endpoint_key, rate_limit)

    def _parse_window(self, window: str) -> timedelta:
        """Parse window string to timedelta."""
        window = window.strip().lower()

        # Match patterns like "1h", "30m", "60s", "1d"
        match = None
        for pattern in ["d", "h", "m", "s"]:
            if window.endswith(pattern):
                try:
                    value = int(window[:-1])
                    if pattern == "d":
                        return timedelta(days=value)
                    elif pattern == "h":
                        return timedelta(hours=value)
                    elif pattern == "m":
                        return timedelta(minutes=value)
                    elif pattern == "s":
                        return timedelta(seconds=value)
                except ValueError:
                    pass

        # Default to 1 hour
        return timedelta(hours=1)

    def clear(self, endpoint: Optional[str] = None) -> None:
        """
        Clear stored rate limit data.

        Args:
            endpoint: Specific endpoint to clear, or None to clear all
        """
        if endpoint:
            if not endpoint.startswith(("http://", "https://")):
                endpoint = f"https://{endpoint}"
            endpoint_key = self._get_endpoint_key(endpoint)
            self._storage.clear(endpoint_key)
        else:
            self._storage.clear()

