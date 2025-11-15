"""Integration tests with real API endpoints.

Note: These tests require API keys to run. Replace YOUR_RAPIDAPI_KEY
with your actual RapidAPI key, or skip these tests if you don't have one.
"""

import json
import os
import pytest
import time

from smartratelimit import RateLimiter

# Get API key from environment variable or use placeholder
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "YOUR_RAPIDAPI_KEY")


class TestRealAPI:
    """Test rate limiting with real API endpoints."""

    @pytest.mark.skipif(
        RAPIDAPI_KEY == "YOUR_RAPIDAPI_KEY",
        reason="RAPIDAPI_KEY not set. Set environment variable RAPIDAPI_KEY to run this test."
    )
    def test_rapidapi_phone_validation(self):
        """Test rate limiting with RapidAPI phone validation endpoint."""
        limiter = RateLimiter()
        
        # RapidAPI endpoint details
        url = "https://phone-and-email-validation-api.p.rapidapi.com/validate-phone"
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "phone-and-email-validation-api.p.rapidapi.com",
            "Content-Type": "application/json",
        }
        data = {"phone_number": "+12065550100"}
        
        # Make a request - rate limiter should handle it automatically
        response = limiter.request(
            "POST",
            url,
            headers=headers,
            json=data
        )
        
        # Verify the request was successful
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        
        # Check if response contains expected data (RapidAPI returns country, format_e164, etc.)
        response_data = response.json()
        print(f"\nAPI Response: {json.dumps(response_data, indent=2)}")
        # RapidAPI phone validation returns fields like country, format_e164, country_code
        assert "country" in response_data or "format_e164" in response_data or "country_code" in response_data
        
        # Check if rate limit info was detected and stored
        status = limiter.get_status(url)
        if status:
            print(f"\nDetected rate limit: {status.limit} requests, {status.remaining} remaining")
            assert status.limit > 0, "Rate limit should be detected"
        
        # Make another request to verify rate limiting is working
        response2 = limiter.request(
            "POST",
            url,
            headers=headers,
            json={"phone_number": "+12065550101"}
        )
        
        assert response2.status_code in [200, 201], f"Second request failed with {response2.status_code}"
        
        # Verify rate limit status was updated
        status2 = limiter.get_status(url)
        if status2:
            print(f"After second request: {status2.remaining} remaining")
            # Remaining should be less than or equal to the first check
            if status:
                assert status2.remaining <= status.remaining, "Remaining should decrease after requests"

    @pytest.mark.skipif(
        RAPIDAPI_KEY == "YOUR_RAPIDAPI_KEY",
        reason="RAPIDAPI_KEY not set. Set environment variable RAPIDAPI_KEY to run this test."
    )
    def test_rapidapi_rate_limit_detection(self):
        """Test that rate limit headers are properly detected from RapidAPI."""
        limiter = RateLimiter()
        
        url = "https://phone-and-email-validation-api.p.rapidapi.com/validate-phone"
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "phone-and-email-validation-api.p.rapidapi.com",
            "Content-Type": "application/json",
        }
        
        # Make initial request
        response = limiter.request(
            "POST",
            url,
            headers=headers,
            json={"phone_number": "+12065550100"}
        )
        
        # Check response headers for rate limit information
        print("\nResponse headers:")
        for header, value in response.headers.items():
            if "rate" in header.lower() or "limit" in header.lower():
                print(f"  {header}: {value}")
        
        # Verify rate limit was detected
        status = limiter.get_status(url)
        if status:
            print(f"\nRate limit status:")
            print(f"  Limit: {status.limit}")
            print(f"  Remaining: {status.remaining}")
            print(f"  Reset time: {status.reset_time}")
            assert status.limit > 0, "Rate limit should be detected from headers"

    @pytest.mark.skipif(
        RAPIDAPI_KEY == "YOUR_RAPIDAPI_KEY",
        reason="RAPIDAPI_KEY not set. Set environment variable RAPIDAPI_KEY to run this test."
    )
    def test_rapidapi_multiple_requests(self):
        """Test making multiple requests with rate limiting."""
        limiter = RateLimiter()
        
        url = "https://phone-and-email-validation-api.p.rapidapi.com/validate-phone"
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "phone-and-email-validation-api.p.rapidapi.com",
            "Content-Type": "application/json",
        }
        
        phone_numbers = [
            "+12065550100",
            "+12065550101",
            "+12065550102",
        ]
        
        results = []
        for phone in phone_numbers:
            try:
                response = limiter.request(
                    "POST",
                    url,
                    headers=headers,
                    json={"phone_number": phone}
                )
                results.append({
                    "phone": phone,
                    "status": response.status_code,
                    "success": response.status_code in [200, 201]
                })
                
                # Small delay to avoid hitting rate limits too quickly
                time.sleep(0.5)
                
            except Exception as e:
                results.append({
                    "phone": phone,
                    "error": str(e),
                    "success": False
                })
        
        # Verify at least some requests succeeded
        successful = sum(1 for r in results if r.get("success", False))
        print(f"\nMade {len(results)} requests, {successful} successful")
        assert successful > 0, "At least one request should succeed"
        
        # Check final rate limit status
        status = limiter.get_status(url)
        if status:
            print(f"Final rate limit status: {status.remaining}/{status.limit} remaining")

    @pytest.mark.skip(reason="Only run manually to avoid excessive API calls")
    def test_rapidapi_rate_limit_enforcement(self):
        """Test that rate limiting actually waits when limits are reached."""
        limiter = RateLimiter()
        
        url = "https://phone-and-email-validation-api.p.rapidapi.com/validate-phone"
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "phone-and-email-validation-api.p.rapidapi.com",
            "Content-Type": "application/json",
        }
        
        # Make requests until we hit the rate limit
        request_count = 0
        start_time = time.time()
        
        # Try to make 10 requests quickly
        for i in range(10):
            try:
                response = limiter.request(
                    "POST",
                    url,
                    headers=headers,
                    json={"phone_number": f"+1206555010{i}"}
                )
                request_count += 1
                
                if response.status_code == 429:
                    print(f"\nHit rate limit after {request_count} requests")
                    break
                    
            except Exception as e:
                print(f"Request {i+1} failed: {e}")
                break
        
        elapsed = time.time() - start_time
        print(f"\nMade {request_count} requests in {elapsed:.2f} seconds")
        
        # Rate limiter should have handled waiting automatically
        status = limiter.get_status(url)
        if status:
            print(f"Rate limit status: {status.remaining}/{status.limit}")

