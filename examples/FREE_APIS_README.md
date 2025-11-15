# Free APIs Testing Examples

This directory contains examples demonstrating `smartratelimit` with various free APIs from [apipheny.io/free-api/](https://apipheny.io/free-api/).

## Examples

### 1. `free_apis_demo.py`
Comprehensive demo testing 10 different free APIs:
- Cat Facts
- Bitcoin Price (CoinDesk)
- Random Activity (Bored API)
- Dog Images
- Random User
- Jokes API
- IPify
- Agify.io (with rate limit detection!)
- Genderize.io (with rate limit detection!)
- Nationalize.io (with rate limit detection!)

**Run:**
```bash
python3 examples/free_apis_demo.py
```

### 2. `free_apis_batch.py`
Batch testing multiple APIs sequentially to demonstrate:
- Automatic rate limit handling
- Error handling
- Performance metrics

**Run:**
```bash
python3 examples/free_apis_batch.py
```

### 3. `free_apis_working.py`
Focused demo on working APIs that demonstrate rate limit detection:
- Shows rate limit headers being detected
- Tracks remaining requests
- Demonstrates rate limit status monitoring

**Run:**
```bash
python3 examples/free_apis_working.py
```

## APIs with Rate Limit Detection

These APIs return rate limit headers that `smartratelimit` automatically detects:

1. **Agify.io** - Predict age from name
   - URL: `https://api.agify.io?name=Michael`
   - Rate limit: 1000 requests/day (free tier)

2. **Genderize.io** - Predict gender from name
   - URL: `https://api.genderize.io?name=Alex`
   - Rate limit: 1000 requests/day (free tier)

3. **Nationalize.io** - Predict nationality from name
   - URL: `https://api.nationalize.io?name=Nathaniel`
   - Rate limit: 1000 requests/day (free tier)

## Quick Start

```python
from smartratelimit import RateLimiter

# Create rate limiter
limiter = RateLimiter()

# Make request - rate limiting is automatic!
url = "https://api.agify.io"
params = {"name": "Michael"}
response = limiter.request("GET", url, params=params)

# Check rate limit status
status = limiter.get_status(url)
if status:
    print(f"Remaining: {status.remaining}/{status.limit}")
```

## Benefits Demonstrated

✅ **Automatic Detection** - Detects rate limits from API response headers  
✅ **No Configuration** - Works out of the box  
✅ **Status Tracking** - Monitor remaining requests  
✅ **Error Handling** - Gracefully handles API errors  
✅ **Multi-API Support** - Works with any API that returns rate limit headers  

## Notes

- Some APIs may be temporarily unavailable (Cat Facts, CoinDesk, Bored API)
- Rate limit detection works when APIs return standard rate limit headers
- APIs without rate limit headers still work, but limits won't be automatically detected
- You can manually set limits: `limiter.set_limit("api.example.com", limit=100, window="1h")`

## References

- [Free APIs List](https://apipheny.io/free-api/)
- [smartratelimit Documentation](../README.md)

