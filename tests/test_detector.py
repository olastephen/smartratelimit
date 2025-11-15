"""Tests for rate limit detection."""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from smartratelimit.detector import RateLimitDetector


class TestRateLimitDetector:
    """Test RateLimitDetector."""

    def test_detect_standard_headers(self):
        """Test detection of standard rate limit headers."""
        detector = RateLimitDetector()

        response = Mock()
        response.url = "https://api.example.com/test"
        response.headers = {
            "X-RateLimit-Limit": "100",
            "X-RateLimit-Remaining": "50",
            "X-RateLimit-Reset": "1640995200",  # Unix timestamp
        }

        result = detector.detect_from_response(response)
        assert result is not None
        assert result["limit"] == 100
        assert result["remaining"] == 50
        assert isinstance(result["reset_time"], datetime)

    def test_detect_github_headers(self):
        """Test detection of GitHub-style headers."""
        detector = RateLimitDetector()

        response = Mock()
        response.url = "https://api.github.com/users"
        response.status_code = 200
        response.headers = {
            "X-RateLimit-Limit": "5000",
            "X-RateLimit-Remaining": "4999",
            "X-RateLimit-Reset": "1640995200",
        }

        result = detector.detect_from_response(response)
        assert result is not None
        assert result["limit"] == 5000
        assert result["remaining"] == 4999

    def test_detect_429_with_retry_after(self):
        """Test detection from 429 response with Retry-After."""
        detector = RateLimitDetector()

        response = Mock()
        response.url = "https://api.example.com/test"
        response.status_code = 429
        response.headers = {
            "Retry-After": "60",
        }

        result = detector.detect_from_response(response)
        assert result is not None
        assert result["remaining"] == 0
        assert isinstance(result["reset_time"], datetime)

    def test_detect_custom_headers(self):
        """Test detection with custom header mapping."""
        detector = RateLimitDetector(
            custom_headers_map={
                "limit": "X-My-API-Limit",
                "remaining": "X-My-API-Remaining",
                "reset": "X-My-API-Reset",
            }
        )

        response = Mock()
        response.url = "https://api.example.com/test"
        response.headers = {
            "X-My-API-Limit": "200",
            "X-My-API-Remaining": "150",
            "X-My-API-Reset": "1640995200",
        }

        result = detector.detect_from_response(response)
        assert result is not None
        assert result["limit"] == 200
        assert result["remaining"] == 150

    def test_no_detection(self):
        """Test when no rate limit headers are present."""
        detector = RateLimitDetector()

        response = Mock()
        response.url = "https://api.example.com/test"
        response.status_code = 200
        response.headers = {}

        result = detector.detect_from_response(response)
        assert result is None

    def test_parse_reset_time_unix(self):
        """Test parsing Unix timestamp reset time."""
        detector = RateLimitDetector()

        reset_time, window = detector._parse_reset_time("1640995200", "api.example.com")
        assert isinstance(reset_time, datetime)
        assert isinstance(window, timedelta)

    def test_parse_reset_time_relative(self):
        """Test parsing relative seconds reset time."""
        detector = RateLimitDetector()

        # Use a value that's clearly a relative time (not a Unix timestamp)
        # Unix timestamps are typically > 1000000000 (year 2001+)
        # So use a small number that's clearly relative seconds
        reset_time, window = detector._parse_reset_time("30", "api.example.com")
        assert isinstance(reset_time, datetime)
        assert isinstance(window, timedelta)
        # Allow some tolerance for timing
        assert 25 < window.total_seconds() < 35

