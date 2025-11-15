# Quick Start Guide

Get started with smartratelimit in 5 minutes!

## Installation

```bash
pip install smartratelimit
```

For async support:
```bash
pip install smartratelimit[httpx]    # For httpx
pip install smartratelimit[aiohttp]  # For aiohttp
pip install smartratelimit[all]      # For all optional dependencies
```

## Your First Request

```python
from smartratelimit import RateLimiter

# Create a rate limiter
limiter = RateLimiter()

# Make a request - rate limiting is automatic!
response = limiter.request('GET', 'https://api.github.com/users/octocat')
print(response.json())
```

That's it! The library automatically:
- ✅ Detects rate limits from API headers
- ✅ Tracks remaining requests
- ✅ Waits when limits are reached
- ✅ Updates limits from each response

## Example: Using Free APIs

### Random User API (No Key Required)

```python
from smartratelimit import RateLimiter

limiter = RateLimiter()
url = "https://randomuser.me/api/"

# Get random user data
response = limiter.request("GET", url)
data = response.json()

user = data["results"][0]
print(f"Name: {user['name']['first']} {user['name']['last']}")
print(f"Email: {user['email']}")
print(f"Location: {user['location']['city']}")

# Check rate limit status
status = limiter.get_status(url)
if status:
    print(f"Rate limit: {status.remaining}/{status.limit} remaining")
```

### Dog Images API

```python
from smartratelimit import RateLimiter

limiter = RateLimiter()

# Get random dog image
response = limiter.request("GET", "https://dog.ceo/api/breeds/image/random")
data = response.json()

print(f"Random dog image: {data['message']}")
```

### Jokes API

```python
from smartratelimit import RateLimiter

limiter = RateLimiter()

# Get a random joke
response = limiter.request("GET", "https://official-joke-api.appspot.com/random_joke")
joke = response.json()

print(f"Setup: {joke['setup']}")
print(f"Punchline: {joke['punchline']}")
```

### IP Address Lookup

```python
from smartratelimit import RateLimiter

limiter = RateLimiter()

# Get your IP address
response = limiter.request("GET", "https://api.ipify.org?format=json")
data = response.json()

print(f"Your IP: {data['ip']}")
```

## Example: APIs with Rate Limit Detection

### Agify.io - Predict Age from Name

```python
from smartratelimit import RateLimiter

limiter = RateLimiter()

# Predict age from name (has rate limits!)
url = "https://api.agify.io"
params = {"name": "Michael"}

response = limiter.request("GET", url, params=params)
data = response.json()

print(f"Name: {data['name']}")
print(f"Predicted Age: {data['age']}")
print(f"Based on {data['count']} occurrences")

# Check rate limit (this API returns rate limit headers!)
status = limiter.get_status(url)
if status:
    print(f"\nRate Limit Status:")
    print(f"  Remaining: {status.remaining}/{status.limit}")
    print(f"  Resets in: {status.reset_in:.0f} seconds")
```

### Genderize.io - Predict Gender

```python
from smartratelimit import RateLimiter

limiter = RateLimiter()

url = "https://api.genderize.io"
params = {"name": "Alex"}

response = limiter.request("GET", url, params=params)
data = response.json()

print(f"Name: {data['name']}")
print(f"Gender: {data['gender']} ({data['probability'] * 100:.1f}% confidence)")

# Rate limit is automatically tracked
status = limiter.get_status(url)
if status:
    print(f"Rate limit: {status.remaining}/{status.limit} remaining")
```

### Nationalize.io - Predict Nationality

```python
from smartratelimit import RateLimiter

limiter = RateLimiter()

url = "https://api.nationalize.io"
params = {"name": "Nathaniel"}

response = limiter.request("GET", url, params=params)
data = response.json()

print(f"Name: {data['name']}")
countries = data['country']
if countries:
    top = countries[0]
    print(f"Top Nationality: {top['country_id']} ({top['probability'] * 100:.1f}%)")
```

## Making Multiple Requests

```python
from smartratelimit import RateLimiter

limiter = RateLimiter()

# Process multiple items - rate limiting is automatic!
names = ["Sarah", "John", "Emma", "David", "Lisa"]
url = "https://api.agify.io"

for name in names:
    response = limiter.request("GET", url, params={"name": name})
    data = response.json()
    print(f"{name}: Age {data['age']}")
    
    # Check remaining requests
    status = limiter.get_status(url)
    if status:
        print(f"  Remaining: {status.remaining}/{status.limit}\n")
```

## Next Steps

- 📖 [Complete Tutorial](TUTORIAL.md) - Detailed step-by-step guide
- 📚 [API Reference](API_REFERENCE.md) - Complete API documentation
- 💾 [Storage Backends](STORAGE_BACKENDS.md) - SQLite and Redis setup
- ⚡ [Async Guide](ASYNC_GUIDE.md) - Async/await usage
- 🔄 [Retry Strategies](RETRY_STRATEGIES.md) - Advanced retry logic
- 📊 [Metrics Guide](METRICS_GUIDE.md) - Collecting and exporting metrics
- 🛠️ [CLI Guide](CLI_GUIDE.md) - Command-line tools
- 🎯 [Examples](EXAMPLES.md) - More real-world examples

