"""Tests for retry logic."""

import time
from unittest.mock import Mock, patch

import pytest

from smartratelimit.retry import RetryConfig, RetryHandler, RetryStrategy


class TestRetryConfig:
    """Test RetryConfig."""

    def test_init_default(self):
        """Test default initialization."""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.strategy == RetryStrategy.EXPONENTIAL
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.backoff_factor == 2.0
        assert 429 in config.retry_on_status

    def test_init_custom(self):
        """Test custom initialization."""
        config = RetryConfig(
            max_retries=5,
            strategy=RetryStrategy.LINEAR,
            base_delay=2.0,
            max_delay=30.0,
            backoff_factor=1.5,
            retry_on_status=[429, 503],
        )
        assert config.max_retries == 5
        assert config.strategy == RetryStrategy.LINEAR
        assert config.base_delay == 2.0
        assert config.max_delay == 30.0
        assert config.backoff_factor == 1.5
        assert config.retry_on_status == [429, 503]


class TestRetryHandler:
    """Test RetryHandler."""

    def test_calculate_delay_exponential(self):
        """Test exponential delay calculation."""
        config = RetryConfig(
            strategy=RetryStrategy.EXPONENTIAL, base_delay=1.0, backoff_factor=2.0
        )
        handler = RetryHandler(config)

        assert handler._calculate_delay(1) == 1.0
        assert handler._calculate_delay(2) == 2.0
        assert handler._calculate_delay(3) == 4.0
        assert handler._calculate_delay(4) == 8.0

    def test_calculate_delay_linear(self):
        """Test linear delay calculation."""
        config = RetryConfig(
            strategy=RetryStrategy.LINEAR, base_delay=2.0
        )
        handler = RetryHandler(config)

        assert handler._calculate_delay(1) == 2.0
        assert handler._calculate_delay(2) == 4.0
        assert handler._calculate_delay(3) == 6.0

    def test_calculate_delay_fixed(self):
        """Test fixed delay calculation."""
        config = RetryConfig(
            strategy=RetryStrategy.FIXED, base_delay=5.0
        )
        handler = RetryHandler(config)

        assert handler._calculate_delay(1) == 5.0
        assert handler._calculate_delay(2) == 5.0
        assert handler._calculate_delay(3) == 5.0

    def test_calculate_delay_max_limit(self):
        """Test delay respects max_delay."""
        config = RetryConfig(
            strategy=RetryStrategy.EXPONENTIAL,
            base_delay=1.0,
            backoff_factor=10.0,
            max_delay=5.0,
        )
        handler = RetryHandler(config)

        assert handler._calculate_delay(1) == 1.0
        assert handler._calculate_delay(2) == 5.0  # Capped at max_delay

    def test_should_retry(self):
        """Test should_retry logic."""
        config = RetryConfig(max_retries=3, retry_on_status=[429, 503])
        handler = RetryHandler(config)

        assert handler.should_retry(429, 1) is True
        assert handler.should_retry(503, 2) is True
        assert handler.should_retry(200, 1) is False
        assert handler.should_retry(429, 4) is False  # Exceeded max_retries

    def test_retry_sync_success(self):
        """Test successful retry (no retries needed)."""
        handler = RetryHandler(RetryConfig())

        mock_response = Mock()
        mock_response.status_code = 200

        def func():
            return mock_response

        result = handler.retry_sync(func)
        assert result.status_code == 200

    def test_retry_sync_with_retries(self):
        """Test retry with multiple attempts."""
        config = RetryConfig(
            max_retries=3,
            strategy=RetryStrategy.FIXED,
            base_delay=0.01,  # Short delay for testing
        )
        handler = RetryHandler(config)

        attempts = []

        def func():
            attempts.append(1)
            response = Mock()
            if len(attempts) < 3:
                response.status_code = 429
            else:
                response.status_code = 200
            return response

        result = handler.retry_sync(func)
        assert result.status_code == 200
        assert len(attempts) == 3

    def test_retry_sync_max_retries_exceeded(self):
        """Test retry when max retries exceeded."""
        config = RetryConfig(
            max_retries=2,
            strategy=RetryStrategy.FIXED,
            base_delay=0.01,
        )
        handler = RetryHandler(config)

        def func():
            response = Mock()
            response.status_code = 429
            return response

        result = handler.retry_sync(func)
        assert result.status_code == 429

    def test_retry_sync_exception(self):
        """Test retry with exceptions."""
        config = RetryConfig(
            max_retries=2,
            strategy=RetryStrategy.FIXED,
            base_delay=0.01,
        )
        handler = RetryHandler(config)

        attempts = []

        def func():
            attempts.append(1)
            if len(attempts) < 2:
                raise ConnectionError("Connection failed")
            return Mock(status_code=200)

        result = handler.retry_sync(func)
        assert result.status_code == 200
        assert len(attempts) == 2

    def test_retry_sync_exception_max_retries(self):
        """Test retry with exception exceeding max retries."""
        config = RetryConfig(
            max_retries=2,
            strategy=RetryStrategy.FIXED,
            base_delay=0.01,
        )
        handler = RetryHandler(config)

        def func():
            raise ConnectionError("Connection failed")

        with pytest.raises(ConnectionError):
            handler.retry_sync(func)

    @pytest.mark.asyncio
    async def test_retry_async_success(self):
        """Test successful async retry."""
        handler = RetryHandler(RetryConfig())

        mock_response = Mock()
        mock_response.status_code = 200

        async def func():
            return mock_response

        result = await handler.retry_async(func)
        assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_retry_async_with_retries(self):
        """Test async retry with multiple attempts."""
        import asyncio

        config = RetryConfig(
            max_retries=3,
            strategy=RetryStrategy.FIXED,
            base_delay=0.01,
        )
        handler = RetryHandler(config)

        attempts = []

        async def func():
            attempts.append(1)
            response = Mock()
            if len(attempts) < 3:
                response.status_code = 429
            else:
                response.status_code = 200
            return response

        result = await handler.retry_async(func)
        assert result.status_code == 200
        assert len(attempts) == 3

