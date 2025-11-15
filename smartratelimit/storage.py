"""Storage backends for rate limit state."""

import sqlite3
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Optional
from urllib.parse import urlparse

from smartratelimit.models import RateLimit, TokenBucket


class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def get_rate_limit(self, endpoint: str) -> Optional[RateLimit]:
        """Get rate limit for an endpoint."""
        pass

    @abstractmethod
    def set_rate_limit(self, endpoint: str, rate_limit: RateLimit) -> None:
        """Store rate limit for an endpoint."""
        pass

    @abstractmethod
    def get_token_bucket(self, key: str) -> Optional[TokenBucket]:
        """Get token bucket for a key."""
        pass

    @abstractmethod
    def set_token_bucket(self, key: str, bucket: TokenBucket) -> None:
        """Store token bucket for a key."""
        pass

    @abstractmethod
    def clear(self, endpoint: Optional[str] = None) -> None:
        """Clear stored data for endpoint or all data."""
        pass


class MemoryStorage(StorageBackend):
    """In-memory storage backend with automatic cleanup."""

    def __init__(self, cleanup_interval: int = 3600):
        """
        Initialize in-memory storage.

        Args:
            cleanup_interval: Seconds between cleanup of expired entries
        """
        self._rate_limits: Dict[str, RateLimit] = {}
        self._token_buckets: Dict[str, TokenBucket] = {}
        self._lock = threading.RLock()
        self._cleanup_interval = cleanup_interval
        self._last_cleanup = datetime.utcnow()

    def _get_endpoint_key(self, url: str) -> str:
        """Extract endpoint key from URL."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _cleanup_expired(self) -> None:
        """Remove expired rate limit entries."""
        now = datetime.utcnow()
        if (now - self._last_cleanup).total_seconds() < self._cleanup_interval:
            return

        # Use list comprehension for better performance
        expired_keys = [
            key for key, rate_limit in self._rate_limits.items()
            if rate_limit.reset_time < now
        ]

        for key in expired_keys:
            self._rate_limits.pop(key, None)

        self._last_cleanup = now

    def get_rate_limit(self, endpoint: str) -> Optional[RateLimit]:
        """Get rate limit for an endpoint."""
        with self._lock:
            self._cleanup_expired()
            return self._rate_limits.get(endpoint)

    def set_rate_limit(self, endpoint: str, rate_limit: RateLimit) -> None:
        """Store rate limit for an endpoint."""
        with self._lock:
            self._rate_limits[endpoint] = rate_limit
            self._cleanup_expired()

    def get_token_bucket(self, key: str) -> Optional[TokenBucket]:
        """Get token bucket for a key."""
        with self._lock:
            return self._token_buckets.get(key)

    def set_token_bucket(self, key: str, bucket: TokenBucket) -> None:
        """Store token bucket for a key."""
        with self._lock:
            self._token_buckets[key] = bucket

    def clear(self, endpoint: Optional[str] = None) -> None:
        """Clear stored data for endpoint or all data."""
        with self._lock:
            if endpoint:
                self._rate_limits.pop(endpoint, None)
                # Clear all token buckets for this endpoint
                keys_to_remove = [
                    k for k in self._token_buckets.keys() if k.startswith(endpoint)
                ]
                for key in keys_to_remove:
                    del self._token_buckets[key]
            else:
                self._rate_limits.clear()
                self._token_buckets.clear()


class SQLiteStorage(StorageBackend):
    """SQLite-based persistent storage backend."""

    def __init__(self, db_path: str = ":memory:"):
        """
        Initialize SQLite storage.

        Args:
            db_path: Path to SQLite database file, or ":memory:" for in-memory DB
        """
        self.db_path = db_path
        self._lock = threading.RLock()
        # For in-memory databases, we need to keep a connection open
        if db_path == ":memory:":
            self._conn = sqlite3.connect(db_path, check_same_thread=False)
            self._init_db(self._conn)
        else:
            self._conn = None
            self._init_db()

    def _init_db(self, conn: Optional[sqlite3.Connection] = None) -> None:
        """Initialize database tables."""
        if conn is None:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            close_conn = True
        else:
            close_conn = False

        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS rate_limits (
                    endpoint TEXT PRIMARY KEY,
                    limit_value INTEGER NOT NULL,
                    remaining INTEGER NOT NULL,
                    reset_time TEXT NOT NULL,
                    window_seconds REAL NOT NULL,
                    last_updated TEXT NOT NULL
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS token_buckets (
                    key TEXT PRIMARY KEY,
                    capacity REAL NOT NULL,
                    tokens REAL NOT NULL,
                    refill_rate REAL NOT NULL,
                    last_update TEXT NOT NULL
                )
            """
            )
            conn.commit()
        finally:
            if close_conn:
                conn.close()

    def _datetime_to_str(self, dt: datetime) -> str:
        """Convert datetime to ISO format string."""
        return dt.isoformat()

    def _str_to_datetime(self, s: str) -> datetime:
        """Convert ISO format string to datetime."""
        return datetime.fromisoformat(s)

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection, reusing for in-memory DB."""
        if self._conn is not None:
            return self._conn
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def get_rate_limit(self, endpoint: str) -> Optional[RateLimit]:
        """Get rate limit for an endpoint."""
        with self._lock:
            conn = self._get_connection()
            try:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM rate_limits WHERE endpoint = ?", (endpoint,)
                )
                row = cursor.fetchone()
                if row is None:
                    return None

                return RateLimit(
                    endpoint=row["endpoint"],
                    limit=row["limit_value"],
                    remaining=row["remaining"],
                    reset_time=self._str_to_datetime(row["reset_time"]),
                    window=timedelta(seconds=row["window_seconds"]),
                    last_updated=self._str_to_datetime(row["last_updated"]),
                )
            finally:
                if self._conn is None:
                    conn.close()

    def set_rate_limit(self, endpoint: str, rate_limit: RateLimit) -> None:
        """Store rate limit for an endpoint."""
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO rate_limits
                    (endpoint, limit_value, remaining, reset_time, window_seconds, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        endpoint,
                        rate_limit.limit,
                        rate_limit.remaining,
                        self._datetime_to_str(rate_limit.reset_time),
                        rate_limit.window.total_seconds(),
                        self._datetime_to_str(rate_limit.last_updated),
                    ),
                )
                conn.commit()
            finally:
                if self._conn is None:
                    conn.close()

    def get_token_bucket(self, key: str) -> Optional[TokenBucket]:
        """Get token bucket for a key."""
        with self._lock:
            conn = self._get_connection()
            try:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM token_buckets WHERE key = ?", (key,)
                )
                row = cursor.fetchone()
                if row is None:
                    return None

                return TokenBucket(
                    capacity=row["capacity"],
                    tokens=row["tokens"],
                    refill_rate=row["refill_rate"],
                    last_update=self._str_to_datetime(row["last_update"]),
                )
            finally:
                if self._conn is None:
                    conn.close()

    def set_token_bucket(self, key: str, bucket: TokenBucket) -> None:
        """Store token bucket for a key."""
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO token_buckets
                    (key, capacity, tokens, refill_rate, last_update)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        key,
                        bucket.capacity,
                        bucket.tokens,
                        bucket.refill_rate,
                        self._datetime_to_str(bucket.last_update),
                    ),
                )
                conn.commit()
            finally:
                if self._conn is None:
                    conn.close()

    def clear(self, endpoint: Optional[str] = None) -> None:
        """Clear stored data for endpoint or all data."""
        with self._lock:
            conn = self._get_connection()
            try:
                if endpoint:
                    conn.execute(
                        "DELETE FROM rate_limits WHERE endpoint = ?", (endpoint,)
                    )
                    conn.execute(
                        "DELETE FROM token_buckets WHERE key LIKE ?",
                        (f"{endpoint}%",),
                    )
                else:
                    conn.execute("DELETE FROM rate_limits")
                    conn.execute("DELETE FROM token_buckets")
                conn.commit()
            finally:
                if self._conn is None:
                    conn.close()


class RedisStorage(StorageBackend):
    """Redis-based distributed storage backend."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0", key_prefix: str = "ratelimit:"):
        """
        Initialize Redis storage.

        Args:
            redis_url: Redis connection URL
            key_prefix: Prefix for all keys stored in Redis
        """
        try:
            import redis
        except ImportError:
            raise ImportError(
                "Redis support requires the 'redis' package. "
                "Install it with: pip install redis"
            )

        self.redis_client = redis.from_url(redis_url, decode_responses=False)
        self.key_prefix = key_prefix
        self._lock = threading.RLock()

    def _make_key(self, key: str) -> bytes:
        """Create a Redis key with prefix."""
        return f"{self.key_prefix}{key}".encode("utf-8")

    def _datetime_to_str(self, dt: datetime) -> str:
        """Convert datetime to ISO format string."""
        return dt.isoformat()

    def _str_to_datetime(self, s: bytes) -> datetime:
        """Convert bytes to datetime."""
        return datetime.fromisoformat(s.decode("utf-8"))

    def get_rate_limit(self, endpoint: str) -> Optional[RateLimit]:
        """Get rate limit for an endpoint."""
        with self._lock:
            try:
                key = self._make_key(f"rate_limit:{endpoint}")
                data = self.redis_client.hgetall(key)
                if not data:
                    return None

                return RateLimit(
                    endpoint=endpoint,
                    limit=int(data[b"limit"]),
                    remaining=int(data[b"remaining"]),
                    reset_time=self._str_to_datetime(data[b"reset_time"]),
                    window=timedelta(seconds=float(data[b"window_seconds"])),
                    last_updated=self._str_to_datetime(data[b"last_updated"]),
                )
            except Exception:
                return None

    def set_rate_limit(self, endpoint: str, rate_limit: RateLimit) -> None:
        """Store rate limit for an endpoint."""
        with self._lock:
            try:
                key = self._make_key(f"rate_limit:{endpoint}")
                data = {
                    b"limit": str(rate_limit.limit).encode("utf-8"),
                    b"remaining": str(rate_limit.remaining).encode("utf-8"),
                    b"reset_time": self._datetime_to_str(rate_limit.reset_time).encode("utf-8"),
                    b"window_seconds": str(rate_limit.window.total_seconds()).encode("utf-8"),
                    b"last_updated": self._datetime_to_str(rate_limit.last_updated).encode("utf-8"),
                }
                self.redis_client.hset(key, mapping=data)
                # Set expiration to window + 1 hour for cleanup
                ttl = int((rate_limit.window + timedelta(hours=1)).total_seconds())
                self.redis_client.expire(key, ttl)
            except Exception:
                pass  # Graceful degradation

    def get_token_bucket(self, key: str) -> Optional[TokenBucket]:
        """Get token bucket for a key."""
        with self._lock:
            try:
                redis_key = self._make_key(f"token_bucket:{key}")
                data = self.redis_client.hgetall(redis_key)
                if not data:
                    return None

                return TokenBucket(
                    capacity=float(data[b"capacity"]),
                    tokens=float(data[b"tokens"]),
                    refill_rate=float(data[b"refill_rate"]),
                    last_update=self._str_to_datetime(data[b"last_update"]),
                )
            except Exception:
                return None

    def set_token_bucket(self, key: str, bucket: TokenBucket) -> None:
        """Store token bucket for a key."""
        with self._lock:
            try:
                redis_key = self._make_key(f"token_bucket:{key}")
                data = {
                    b"capacity": str(bucket.capacity).encode("utf-8"),
                    b"tokens": str(bucket.tokens).encode("utf-8"),
                    b"refill_rate": str(bucket.refill_rate).encode("utf-8"),
                    b"last_update": self._datetime_to_str(bucket.last_update).encode("utf-8"),
                }
                self.redis_client.hset(redis_key, mapping=data)
                # Set expiration to 24 hours for cleanup
                self.redis_client.expire(redis_key, 86400)
            except Exception:
                pass  # Graceful degradation

    def clear(self, endpoint: Optional[str] = None) -> None:
        """Clear stored data for endpoint or all data."""
        with self._lock:
            try:
                if endpoint:
                    # Delete rate limit
                    rate_limit_key = self._make_key(f"rate_limit:{endpoint}")
                    self.redis_client.delete(rate_limit_key)
                    # Delete token buckets for this endpoint
                    pattern = self._make_key(f"token_bucket:{endpoint}*")
                    for key in self.redis_client.scan_iter(match=pattern):
                        self.redis_client.delete(key)
                else:
                    # Delete all keys with prefix
                    pattern = self._make_key("*")
                    for key in self.redis_client.scan_iter(match=pattern):
                        self.redis_client.delete(key)
            except Exception:
                pass  # Graceful degradation

