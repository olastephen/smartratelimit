"""
Example: Integrating smartratelimit with RapidAPI email validation.

This shows how to convert your http.client code to use smartratelimit.
"""

# ============================================================================
# OPTION 1: Using requests (RECOMMENDED - Easiest integration)
# ============================================================================

from smartratelimit import RateLimiter

# Create a rate limiter (automatically detects and manages rate limits)
limiter = RateLimiter()

# Your original code converted to use requests + smartratelimit
url = "https://phone-and-email-validation-api.p.rapidapi.com/validate-email"
headers = {
    'x-rapidapi-key': "YOUR_RAPIDAPI_KEY",  # Get from https://rapidapi.com
    'x-rapidapi-host': "phone-and-email-validation-api.p.rapidapi.com",
    'Content-Type': "application/json"
}
payload = {"email": "info@facebook.com"}

# Make the request - rate limiting is automatic!
response = limiter.request("POST", url, headers=headers, json=payload)

# Get the response data
data = response.text
print(data)

# Rate limit status is automatically tracked
status = limiter.get_status(url)
if status:
    print(f"\nRate Limit Status:")
    print(f"  Limit: {status.limit}")
    print(f"  Remaining: {status.remaining}")
    print(f"  Resets in: {status.reset_in:.0f} seconds")


# ============================================================================
# OPTION 2: Using http.client (More complex - requires wrapping)
# ============================================================================

import http.client
from smartratelimit import RateLimiter
import json

def make_rate_limited_request(limiter, method, url, headers=None, payload=None):
    """
    Wrapper function to use http.client with smartratelimit.
    
    Note: This is more complex. Option 1 (using requests) is recommended.
    """
    from urllib.parse import urlparse
    
    # Parse the URL
    parsed = urlparse(url)
    host = parsed.netloc
    path = parsed.path or "/"
    
    # Check rate limit before making request
    endpoint_key = f"https://{host}"
    status = limiter.get_status(endpoint_key)
    
    if status and status.is_exceeded:
        # Wait if rate limit is exceeded
        wait_time = status.reset_in
        if wait_time > 0:
            import time
            print(f"Rate limit exceeded. Waiting {wait_time:.0f} seconds...")
            time.sleep(wait_time)
    
    # Make the actual request
    conn = http.client.HTTPSConnection(host)
    
    # Convert payload to string if it's a dict
    if isinstance(payload, dict):
        payload_str = json.dumps(payload)
    else:
        payload_str = payload or ""
    
    conn.request(method, path, payload_str, headers or {})
    res = conn.getresponse()
    data = res.read()
    conn.close()
    
    # Create a mock response object for rate limit detection
    class MockResponse:
        def __init__(self, status_code, headers, text):
            self.status_code = status_code
            self.headers = headers
            self.text = text
            self.url = url
    
    # Update rate limit info from response headers
    mock_response = MockResponse(res.status, dict(res.getheaders()), data.decode("utf-8"))
    detected = limiter._detector.detect_from_response(mock_response)
    
    if detected:
        # Update stored rate limit
        from smartratelimit.models import RateLimit
        from datetime import datetime, timedelta
        
        rate_limit = RateLimit(
            endpoint=endpoint_key,
            limit=detected["limit"],
            remaining=detected["remaining"],
            reset_time=detected["reset_time"],
            window=detected["window"]
        )
        limiter._storage.set_rate_limit(endpoint_key, rate_limit)
    
    return data.decode("utf-8")


# Example using the wrapper
if __name__ == "__main__":
    limiter = RateLimiter()
    
    url = "https://phone-and-email-validation-api.p.rapidapi.com/validate-email"
    headers = {
        'x-rapidapi-key': "YOUR_RAPIDAPI_KEY",  # Get from https://rapidapi.com
        'x-rapidapi-host': "phone-and-email-validation-api.p.rapidapi.com",
        'Content-Type': "application/json"
    }
    payload = {"email": "info@facebook.com"}
    
    # This is more complex - Option 1 is recommended
    data = make_rate_limited_request(limiter, "POST", url, headers, payload)
    print(data)


# ============================================================================
# OPTION 3: Multiple requests with automatic rate limiting
# ============================================================================

def validate_multiple_emails(emails):
    """Validate multiple emails with automatic rate limiting."""
    limiter = RateLimiter()
    
    url = "https://phone-and-email-validation-api.p.rapidapi.com/validate-email"
    headers = {
        'x-rapidapi-key': "YOUR_RAPIDAPI_KEY",  # Get from https://rapidapi.com
        'x-rapidapi-host': "phone-and-email-validation-api.p.rapidapi.com",
        'Content-Type': "application/json"
    }
    
    results = []
    for email in emails:
        try:
            response = limiter.request("POST", url, headers=headers, json={"email": email})
            results.append({
                "email": email,
                "status": response.status_code,
                "data": response.json()
            })
        except Exception as e:
            results.append({
                "email": email,
                "error": str(e)
            })
    
    # Check final rate limit status
    status = limiter.get_status(url)
    if status:
        print(f"\nFinal Rate Limit: {status.remaining}/{status.limit} remaining")
    
    return results


# Example usage
if __name__ == "__main__":
    emails = [
        "info@facebook.com",
        "contact@google.com",
        "support@microsoft.com"
    ]
    
    results = validate_multiple_emails(emails)
    for result in results:
        print(f"\n{result['email']}: {result.get('status', 'Error')}")

