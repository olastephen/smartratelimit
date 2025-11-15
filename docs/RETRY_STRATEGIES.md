# Retry Strategies Guide

Complete guide to using retry logic with smartratelimit.

## Table of Contents

1. [RetryHandler Overview](#retryhandler-overview)
2. [Retry Strategies](#retry-strategies)
3. [RetryConfig Options](#retryconfig-options)
4. [Synchronous Retry](#synchronous-retry)
5. [Async Retry](#async-retry)
6. [Examples](#examples)

## RetryHandler Overview

`RetryHandler` provides configurable retry logic for failed API requests.

### Import

```python
from smartratelimit import RetryHandler, RetryConfig, RetryStrategy
```

## Retry Strategies

### Available Strategies

1. **EXPONENTIAL** - Exponential backoff (default)
2. **LINEAR** - Linear backoff
3. **FIXED** - Fixed delay between retries
4. **NONE** - No retry

### Strategy Comparison

```python
from smartratelimit import RetryHandler, RetryConfig, RetryStrategy

# Exponential backoff: 1s, 2s, 4s, 8s...
config = RetryConfig(
    max_retries=3,
    strategy=RetryStrategy.EXPONENTIAL,
    base_delay=1.0
)

# Linear backoff: 1s, 2s, 3s, 4s...
config = RetryConfig(
    max_retries=3,
    strategy=RetryStrategy.LINEAR,
    base_delay=1.0
)

# Fixed delay: 2s, 2s, 2s, 2s...
config = RetryConfig(
    max_retries=3,
    strategy=RetryStrategy.FIXED,
    base_delay=2.0
)

# No retry
config = RetryConfig(
    max_retries=0,
    strategy=RetryStrategy.NONE
)
```

## RetryConfig Options

### Basic Configuration

```python
from smartratelimit import RetryConfig, RetryStrategy

config = RetryConfig(
    max_retries=3,                    # Maximum number of retries
    strategy=RetryStrategy.EXPONENTIAL,  # Retry strategy
    base_delay=1.0,                   # Base delay in seconds
    max_delay=60.0,                   # Maximum delay between retries
    backoff_multiplier=2.0,           # Multiplier for exponential/linear
    retry_on_status=[429, 500, 502, 503, 504]  # HTTP status codes to retry
)
```

### Advanced Configuration

```python
config = RetryConfig(
    max_retries=5,
    strategy=RetryStrategy.EXPONENTIAL,
    base_delay=0.5,
    max_delay=30.0,
    backoff_multiplier=2.0,
    retry_on_status=[429, 500, 502, 503, 504],
    retry_on_exceptions=[ConnectionError, TimeoutError]
)
```

## Synchronous Retry

### Basic Usage

```python
from smartratelimit import RetryHandler, RetryConfig, RetryStrategy
import requests

# Create retry handler
config = RetryConfig(
    max_retries=3,
    strategy=RetryStrategy.EXPONENTIAL
)
handler = RetryHandler(config)

# Make request with retry
def make_request():
    return requests.get("https://api.example.com/data")

response = handler.retry_sync(make_request)
print(response.json())
```

### Example: Free API with Retry

```python
from smartratelimit import RetryHandler, RetryConfig, RetryStrategy
import requests

config = RetryConfig(
    max_retries=3,
    strategy=RetryStrategy.EXPONENTIAL,
    base_delay=1.0
)
handler = RetryHandler(config)

def get_random_user():
    return requests.get("https://randomuser.me/api/")

try:
    response = handler.retry_sync(get_random_user)
    user = response.json()["results"][0]
    print(f"User: {user['name']['first']} {user['name']['last']}")
except Exception as e:
    print(f"Failed after retries: {e}")
```

### Example: Multiple APIs with Retry

```python
from smartratelimit import RetryHandler, RetryConfig, RetryStrategy
import requests

handler = RetryHandler(RetryConfig(max_retries=3))

apis = [
    ("Random User", lambda: requests.get("https://randomuser.me/api/")),
    ("Dog Image", lambda: requests.get("https://dog.ceo/api/breeds/image/random")),
    ("Joke", lambda: requests.get("https://official-joke-api.appspot.com/random_joke"))
]

for name, request_func in apis:
    try:
        response = handler.retry_sync(request_func)
        print(f"{name}: Success - {response.status_code}")
    except Exception as e:
        print(f"{name}: Failed - {e}")
```

### Example: Custom Retry Logic

```python
from smartratelimit import RetryHandler, RetryConfig, RetryStrategy
import requests

# Custom retry for 429 errors
config = RetryConfig(
    max_retries=5,
    strategy=RetryStrategy.EXPONENTIAL,
    base_delay=2.0,
    max_delay=60.0,
    retry_on_status=[429]  # Only retry on rate limit errors
)
handler = RetryHandler(config)

def make_api_request():
    return requests.get("https://api.example.com/data")

response = handler.retry_sync(make_api_request)
```

## Async Retry

### Basic Usage

```python
import httpx
from smartratelimit import RetryHandler, RetryConfig, RetryStrategy
import asyncio

config = RetryConfig(max_retries=3, strategy=RetryStrategy.EXPONENTIAL)
handler = RetryHandler(config)

async def make_request():
    async with httpx.AsyncClient() as client:
        return await client.get("https://api.example.com/data")

async def main():
    response = await handler.retry_async(make_request)
    print(response.json())

asyncio.run(main())
```

### Example: Async with Free APIs

```python
import httpx
from smartratelimit import RetryHandler, RetryConfig, RetryStrategy
import asyncio

handler = RetryHandler(RetryConfig(max_retries=3))

async def get_random_user():
    async with httpx.AsyncClient() as client:
        return await client.get("https://randomuser.me/api/")

async def get_dog_image():
    async with httpx.AsyncClient() as client:
        return await client.get("https://dog.ceo/api/breeds/image/random")

async def main():
    # Retry both requests
    user_response = await handler.retry_async(get_random_user)
    dog_response = await handler.retry_async(get_dog_image)
    
    user = user_response.json()["results"][0]
    dog = dog_response.json()
    
    print(f"User: {user['name']['first']}")
    print(f"Dog: {dog['message']}")

asyncio.run(main())
```

### Example: Concurrent Async Retries

```python
import httpx
from smartratelimit import RetryHandler, RetryConfig, RetryStrategy
import asyncio

handler = RetryHandler(RetryConfig(max_retries=3))

async def fetch_data(url):
    async with httpx.AsyncClient() as client:
        return await client.get(url)

async def main():
    urls = [
        "https://randomuser.me/api/",
        "https://dog.ceo/api/breeds/image/random",
        "https://official-joke-api.appspot.com/random_joke"
    ]
    
    # Retry all requests concurrently
    tasks = [handler.retry_async(lambda u=url: fetch_data(u)) for url in urls]
    responses = await asyncio.gather(*tasks)
    
    for url, response in zip(urls, responses):
        print(f"{url}: {response.status_code}")

asyncio.run(main())
```

## Examples

### Example: Combining Rate Limiting and Retry

```python
from smartratelimit import RateLimiter, RetryHandler, RetryConfig, RetryStrategy

# Rate limiter
limiter = RateLimiter()

# Retry handler
retry_handler = RetryHandler(RetryConfig(max_retries=3))

def make_rate_limited_request():
    return limiter.request("GET", "https://api.example.com/data")

# Combine rate limiting and retry
response = retry_handler.retry_sync(make_rate_limited_request)
print(response.json())
```

### Example: Different Strategies for Different APIs

```python
from smartratelimit import RetryHandler, RetryConfig, RetryStrategy
import requests

# Fast retry for quick APIs
fast_handler = RetryHandler(RetryConfig(
    max_retries=2,
    strategy=RetryStrategy.FIXED,
    base_delay=0.5
))

# Slow retry for rate-limited APIs
slow_handler = RetryHandler(RetryConfig(
    max_retries=5,
    strategy=RetryStrategy.EXPONENTIAL,
    base_delay=2.0,
    max_delay=60.0
))

# Use fast retry for quick API
def quick_request():
    return requests.get("https://api.ipify.org?format=json")

# Use slow retry for rate-limited API
def slow_request():
    return requests.get("https://api.agify.io?name=Michael")

fast_response = fast_handler.retry_sync(quick_request)
slow_response = slow_handler.retry_sync(slow_request)
```

### Example: Retry with Status Checking

```python
from smartratelimit import RetryHandler, RetryConfig, RetryStrategy
import requests

config = RetryConfig(
    max_retries=3,
    strategy=RetryStrategy.EXPONENTIAL,
    retry_on_status=[429, 500, 502, 503, 504]  # Retry on these status codes
)
handler = RetryHandler(config)

def make_request():
    response = requests.get("https://api.example.com/data")
    # Only retry if status code is in retry_on_status
    if response.status_code in config.retry_on_status:
        raise Exception(f"Status {response.status_code}")
    return response

response = handler.retry_sync(make_request)
```

### Example: Retry with Custom Exception Handling

```python
from smartratelimit import RetryHandler, RetryConfig, RetryStrategy
import requests

config = RetryConfig(
    max_retries=3,
    strategy=RetryStrategy.LINEAR,
    retry_on_exceptions=[ConnectionError, TimeoutError]
)
handler = RetryHandler(config)

def make_request():
    try:
        return requests.get("https://api.example.com/data", timeout=5)
    except (ConnectionError, TimeoutError) as e:
        print(f"Retrying due to: {e}")
        raise

response = handler.retry_sync(make_request)
```

## More Resources

- 📖 [Quick Start Guide](QUICK_START.md)
- 📚 [Complete Tutorial](TUTORIAL.md)
- ⚡ [Async Guide](ASYNC_GUIDE.md)
- 💻 [Examples](EXAMPLES.md)

