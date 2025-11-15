"""
Example: Batch email validation with automatic rate limiting.

This shows how smartratelimit automatically handles rate limits
when making multiple requests.
"""

from smartratelimit import RateLimiter
import json

# Create rate limiter
limiter = RateLimiter()

# Configuration
url = "https://phone-and-email-validation-api.p.rapidapi.com/validate-email"
headers = {
    'x-rapidapi-key': "YOUR_RAPIDAPI_KEY",  # Get from https://rapidapi.com
    'x-rapidapi-host': "phone-and-email-validation-api.p.rapidapi.com",
    'Content-Type': "application/json"
}

# List of emails to validate
emails = [
    "info@facebook.com",
    "contact@google.com",
    "support@microsoft.com",
    "hello@github.com",
    "test@example.com"
]

print("Validating emails with automatic rate limiting...\n")

results = []
for i, email in enumerate(emails, 1):
    try:
        # Make request - rate limiter handles waiting automatically
        response = limiter.request("POST", url, headers=headers, json={"email": email})
        
        # Parse response
        data = response.json()
        results.append({
            "email": email,
            "valid": data.get("is_valid", False),
            "status": response.status_code
        })
        
        print(f"✓ {i}/{len(emails)}: {email} - Valid: {data.get('is_valid', False)}")
        
        # Show rate limit status
        status = limiter.get_status(url)
        if status:
            print(f"  Rate limit: {status.remaining}/{status.limit} remaining\n")
        
    except Exception as e:
        print(f"✗ {i}/{len(emails)}: {email} - Error: {e}\n")
        results.append({
            "email": email,
            "error": str(e)
        })

# Final summary
print("\n" + "="*50)
print("VALIDATION SUMMARY")
print("="*50)

valid_count = sum(1 for r in results if r.get("valid", False))
invalid_count = len(results) - valid_count

print(f"Total: {len(results)}")
print(f"Valid: {valid_count}")
print(f"Invalid: {invalid_count}")

# Final rate limit status
status = limiter.get_status(url)
if status:
    print(f"\nFinal Rate Limit: {status.remaining}/{status.limit} remaining")
    print(f"Utilization: {status.utilization * 100:.1f}%")

