"""
Simple example: Converting your http.client code to use smartratelimit.

This is the direct conversion of your original code.
"""

from smartratelimit import RateLimiter

# Create rate limiter - it automatically handles rate limits
limiter = RateLimiter()

# Your original code, converted to use requests + smartratelimit
url = "https://phone-and-email-validation-api.p.rapidapi.com/validate-email"

headers = {
    'x-rapidapi-key': "YOUR_RAPIDAPI_KEY",  # Get from https://rapidapi.com
    'x-rapidapi-host': "phone-and-email-validation-api.p.rapidapi.com",
    'Content-Type': "application/json"
}

payload = {"email": "info@facebook.com"}

# Make the request - rate limiting is handled automatically!
response = limiter.request("POST", url, headers=headers, json=payload)

# Get response data (same as your original code)
data = response.text
print(data)

# Bonus: Check rate limit status
status = limiter.get_status(url)
if status:
    print(f"\n📊 Rate Limit Status:")
    print(f"   Remaining: {status.remaining}/{status.limit}")
    print(f"   Resets in: {status.reset_in:.0f} seconds")

