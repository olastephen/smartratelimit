"""Rate limit detection from HTTP headers."""

import re
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

import requests


class RateLimitDetector:
    """Detects rate limits from HTTP response headers."""

    # Common header patterns
    HEADER_PATTERNS = {
        # Standard patterns
        "limit": [
            "X-RateLimit-Limit",
            "X-RateLimit-Requests-Limit",  # RapidAPI pattern
            "RateLimit-Limit",
            "X-Rate-Limit-Limit",
        ],
        "remaining": [
            "X-RateLimit-Remaining",
            "X-RateLimit-Requests-Remaining",  # RapidAPI pattern
            "RateLimit-Remaining",
            "X-Rate-Limit-Remaining",
        ],
        "reset": [
            "X-RateLimit-Reset",
            "X-RateLimit-Requests-Reset",  # RapidAPI pattern
            "RateLimit-Reset",
            "X-Rate-Limit-Reset",
        ],
        "retry_after": [
            "Retry-After",
            "X-Retry-After",
        ],
    }

    # API-specific patterns
    API_PATTERNS = {
        "github.com": {
            "limit": "X-RateLimit-Limit",
            "remaining": "X-RateLimit-Remaining",
            "reset": "X-RateLimit-Reset",  # Unix timestamp
        },
        "api.stripe.com": {
            "limit": "Stripe-RateLimit-Limit",
            "remaining": "Stripe-RateLimit-Remaining",
            "reset": "Stripe-RateLimit-Reset",
        },
        "api.twitter.com": {
            "limit": "x-rate-limit-limit",
            "remaining": "x-rate-limit-remaining",
            "reset": "x-rate-limit-reset",  # Unix timestamp
        },
        "api.openai.com": {
            "limit": "x-ratelimit-limit-requests",
            "remaining": "x-ratelimit-remaining-requests",
            "reset": "x-ratelimit-reset-requests",
        },
    }

    def __init__(self, custom_headers_map: Optional[Dict[str, str]] = None):
        """
        Initialize detector with optional custom header mapping.

        Args:
            custom_headers_map: Custom mapping like {'limit': 'X-My-Limit', ...}
        """
        self.custom_headers_map = custom_headers_map or {}

    def detect_from_response(
        self, response: requests.Response
    ) -> Optional[Dict[str, any]]:
        """
        Detect rate limit information from HTTP response.

        Returns:
            Dict with keys: limit, remaining, reset_time, window
            or None if no rate limit info found
        """
        headers = response.headers
        url = response.url

        # Get domain for API-specific patterns
        domain = urlparse(url).netloc.lower()

        # Try API-specific pattern first
        if domain in self.API_PATTERNS:
            pattern = self.API_PATTERNS[domain]
            result = self._extract_with_pattern(headers, pattern, domain)
            if result:
                return result

        # Try custom headers
        if self.custom_headers_map:
            result = self._extract_with_pattern(headers, self.custom_headers_map, domain)
            if result:
                return result

        # Try standard patterns
        for limit_header in self.HEADER_PATTERNS["limit"]:
            if limit_header in headers:
                pattern = {
                    "limit": limit_header,
                    "remaining": self._find_header(
                        headers, self.HEADER_PATTERNS["remaining"]
                    ),
                    "reset": self._find_header(
                        headers, self.HEADER_PATTERNS["reset"]
                    ),
                }
                result = self._extract_with_pattern(headers, pattern, domain)
                if result:
                    return result
                break

        # Try to extract from Retry-After on 429
        if response.status_code == 429:
            retry_after = self._find_header(headers, self.HEADER_PATTERNS["retry_after"])
            if retry_after:
                retry_seconds = self._parse_retry_after(headers[retry_after])
                if retry_seconds:
                    return {
                        "limit": None,
                        "remaining": 0,
                        "reset_time": datetime.utcnow()
                        + timedelta(seconds=retry_seconds),
                        "window": timedelta(seconds=retry_seconds),
                    }

        return None

    def _find_header(self, headers: Dict[str, str], candidates: list) -> Optional[str]:
        """Find first matching header from candidates."""
        for candidate in candidates:
            if candidate in headers:
                return candidate
        return None

    def _extract_with_pattern(
        self, headers: Dict[str, str], pattern: Dict[str, str], domain: str
    ) -> Optional[Dict[str, any]]:
        """Extract rate limit info using a specific header pattern."""
        limit_header = pattern.get("limit")
        remaining_header = pattern.get("remaining")
        reset_header = pattern.get("reset")

        if not limit_header or limit_header not in headers:
            return None

        try:
            limit = int(headers[limit_header])
        except (ValueError, TypeError):
            return None

        remaining = None
        if remaining_header and remaining_header in headers:
            try:
                remaining = int(headers[remaining_header])
            except (ValueError, TypeError):
                pass

        reset_time = None
        window = None

        if reset_header and reset_header in headers:
            reset_value = headers[reset_header]
            reset_time, window = self._parse_reset_time(reset_value, domain)

        # If we have limit but no remaining, assume we haven't hit it yet
        if remaining is None:
            remaining = limit

        # If we have remaining but no reset time, estimate window
        if reset_time is None and limit and remaining is not None:
            # Default to 1 hour window if we can't determine
            window = timedelta(hours=1)
            reset_time = datetime.utcnow() + window

        if limit:
            # Ensure we have a reset_time and window
            if reset_time is None:
                window = timedelta(hours=1)
                reset_time = datetime.utcnow() + window
            elif window is None:
                window = reset_time - datetime.utcnow()
                if window.total_seconds() <= 0:
                    window = timedelta(hours=1)
                    reset_time = datetime.utcnow() + window

            return {
                "limit": limit,
                "remaining": remaining if remaining is not None else limit,
                "reset_time": reset_time,
                "window": window,
            }

        return None

    def _parse_reset_time(
        self, reset_value: str, domain: str
    ) -> Tuple[Optional[datetime], Optional[timedelta]]:
        """Parse reset time from header value."""
        try:
            # Try relative seconds first (if value is small, likely relative)
            # Unix timestamps are typically > 1000000000 (year 2001+)
            seconds = int(reset_value)
            if seconds < 86400:  # Less than 1 day, treat as relative seconds
                reset_time = datetime.utcnow() + timedelta(seconds=seconds)
                return reset_time, timedelta(seconds=seconds)
        except (ValueError, TypeError):
            pass

        try:
            # Try Unix timestamp (seconds) - for larger values
            timestamp = float(reset_value)
            if timestamp > 1000000000:  # Likely a Unix timestamp
                reset_time = datetime.utcfromtimestamp(timestamp)
                window = reset_time - datetime.utcnow()
                if window.total_seconds() > 0:  # Valid future time
                    return reset_time, window
        except (ValueError, TypeError, OSError):
            pass

        try:
            # Try ISO 8601 format
            reset_time = datetime.fromisoformat(reset_value.replace("Z", "+00:00"))
            window = reset_time - datetime.utcnow()
            if window.total_seconds() > 0:  # Valid future time
                return reset_time, window
        except (ValueError, TypeError):
            pass

        # Fallback: try as relative seconds
        try:
            seconds = int(reset_value)
            reset_time = datetime.utcnow() + timedelta(seconds=seconds)
            return reset_time, timedelta(seconds=seconds)
        except (ValueError, TypeError):
            pass

        return None, None

    def _parse_retry_after(self, retry_after: str) -> Optional[int]:
        """Parse Retry-After header value."""
        try:
            # Try as seconds
            return int(retry_after)
        except (ValueError, TypeError):
            pass

        # Try HTTP-date format (RFC 7231)
        try:
            from email.utils import parsedate_to_datetime

            retry_date = parsedate_to_datetime(retry_after)
            delta = retry_date - datetime.utcnow()
            return int(delta.total_seconds())
        except (ValueError, TypeError):
            pass

        return None

