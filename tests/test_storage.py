"""Tests for storage backends."""

import pytest

from smartratelimit.models import RateLimit, TokenBucket
from smartratelimit.storage import MemoryStorage


class TestMemoryStorage:
    """Test MemoryStorage backend."""

    def test_get_set_rate_limit(self):
        """Test storing and retrieving rate limits."""
        storage = MemoryStorage()

        rate_limit = RateLimit(
            endpoint="https://api.example.com",
            limit=100,
            remaining=50,
            reset_time=None,
            window=None,
        )

        storage.set_rate_limit("https://api.example.com", rate_limit)
        retrieved = storage.get_rate_limit("https://api.example.com")

        assert retrieved is not None
        assert retrieved.endpoint == rate_limit.endpoint
        assert retrieved.limit == rate_limit.limit
        assert retrieved.remaining == rate_limit.remaining

    def test_get_nonexistent_rate_limit(self):
        """Test retrieving non-existent rate limit."""
        storage = MemoryStorage()
        result = storage.get_rate_limit("https://api.example.com")
        assert result is None

    def test_get_set_token_bucket(self):
        """Test storing and retrieving token buckets."""
        storage = MemoryStorage()

        bucket = TokenBucket(capacity=10.0, tokens=5.0, refill_rate=1.0)
        storage.set_token_bucket("test_key", bucket)

        retrieved = storage.get_token_bucket("test_key")
        assert retrieved is not None
        assert retrieved.capacity == bucket.capacity
        assert retrieved.tokens == bucket.tokens

    def test_clear_specific_endpoint(self):
        """Test clearing specific endpoint."""
        storage = MemoryStorage()

        rate_limit = RateLimit(
            endpoint="https://api.example.com",
            limit=100,
            remaining=50,
            reset_time=None,
            window=None,
        )
        storage.set_rate_limit("https://api.example.com", rate_limit)
        storage.set_token_bucket("https://api.example.com:default", TokenBucket(10, 5, 1))

        storage.clear("https://api.example.com")

        assert storage.get_rate_limit("https://api.example.com") is None
        assert storage.get_token_bucket("https://api.example.com:default") is None

    def test_clear_all(self):
        """Test clearing all data."""
        storage = MemoryStorage()

        storage.set_rate_limit("https://api1.com", RateLimit("https://api1.com", 100, 50, None, None))
        storage.set_rate_limit("https://api2.com", RateLimit("https://api2.com", 200, 100, None, None))
        storage.set_token_bucket("key1", TokenBucket(10, 5, 1))
        storage.set_token_bucket("key2", TokenBucket(20, 10, 2))

        storage.clear()

        assert storage.get_rate_limit("https://api1.com") is None
        assert storage.get_rate_limit("https://api2.com") is None
        assert storage.get_token_bucket("key1") is None
        assert storage.get_token_bucket("key2") is None

    def test_thread_safety(self):
        """Test thread safety of storage operations."""
        import threading

        storage = MemoryStorage()
        errors = []

        def worker():
            try:
                for i in range(100):
                    rate_limit = RateLimit(
                        endpoint=f"https://api{i}.com",
                        limit=100,
                        remaining=50,
                        reset_time=None,
                        window=None,
                    )
                    storage.set_rate_limit(f"https://api{i}.com", rate_limit)
                    storage.get_rate_limit(f"https://api{i}.com")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0

