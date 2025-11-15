# Tutorial: Getting Started with smartratelimit

A step-by-step guide to using smartratelimit in your projects.

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Advanced Features](#advanced-features)
4. [Best Practices](#best-practices)
5. [Common Patterns](#common-patterns)

## Installation

```bash
pip install smartratelimit
```

For async support:
```bash
pip install smartratelimit[httpx]  # or [aiohttp] or [all]
```

## Basic Usage

### Simple Rate Limiting

The simplest way to use smartratelimit:

```python
from smartratelimit import RateLimiter

limiter = RateLimiter()
response = limiter.request('GET', 'https://api.github.com/users/octocat')
print(response.json())
```

That's it! The library automatically:
- Detects rate limits from response headers
- Tracks remaining requests
- Waits when limits are reached
- Updates limits from each response

### With Default Limits

For APIs that don't provide rate limit headers:

```python
limiter = RateLimiter(
    default_limits={'requests_per_minute': 60}
)

for url in urls:
    response = limiter.request('GET', url)
    # Automatically respects 60 requests/minute limit
```

### Persistent Storage

Save rate limit state across restarts:

```python
# SQLite - single machine
limiter = RateLimiter(storage='sqlite:///rate_limits.db')

# Redis - multiple processes/workers
limiter = RateLimiter(storage='redis://localhost:6379/0')
```

## Advanced Features

### Async Requests

#### With httpx

```python
import httpx
from smartratelimit import AsyncRateLimiter

async def fetch_data():
    async with AsyncRateLimiter() as limiter:
        async with httpx.AsyncClient() as client:
            response = await limiter.arequest_httpx(
                client, 'GET', 'https://api.github.com/users'
            )
            return response.json()

# Run it
import asyncio
data = asyncio.run(fetch_data())
```

#### With aiohttp

```python
import aiohttp
from smartratelimit import AsyncRateLimiter

async def fetch_data():
    async with AsyncRateLimiter() as limiter:
        async with aiohttp.ClientSession() as session:
            response = await limiter.arequest_aiohttp(
                session, 'GET', 'https://api.github.com/users'
            )
            return await response.json()
```

### Retry Logic

Handle transient failures automatically:

```python
from smartratelimit import RateLimiter
from smartratelimit.retry import RetryConfig, RetryHandler, RetryStrategy

limiter = RateLimiter()

# Configure retry with exponential backoff
retry_config = RetryConfig(
    max_retries=3,
    strategy=RetryStrategy.EXPONENTIAL,
    base_delay=1.0,
    backoff_factor=2.0,
)

retry_handler = RetryHandler(retry_config)

def make_request():
    return limiter.request('GET', 'https://api.example.com/data')

# Automatically retries on 429, 503, 504
response = retry_handler.retry_sync(make_request)
```

### Metrics Collection

Track your API usage:

```python
from smartratelimit import RateLimiter
from smartratelimit.metrics import MetricsCollector

limiter = RateLimiter()
metrics = MetricsCollector()

# Make requests
for url in urls:
    response = limiter.request('GET', url)
    status = limiter.get_status(url)
    metrics.record_request(url, response.status_code, status)

# Export Prometheus metrics
prometheus_metrics = metrics.export_prometheus()
print(prometheus_metrics)

# Or export as JSON
json_metrics = metrics.export_json()
```

## Best Practices

### 1. Use Persistent Storage in Production

```python
# Good for production
limiter = RateLimiter(storage='sqlite:///rate_limits.db')

# Or for distributed systems
limiter = RateLimiter(storage='redis://localhost:6379/0')
```

### 2. Set Default Limits

Always set default limits for APIs without headers:

```python
limiter = RateLimiter(
    default_limits={'requests_per_minute': 60}
)
```

### 3. Monitor Rate Limits

Check status before making many requests:

```python
status = limiter.get_status('api.example.com')
if status and status.utilization > 0.9:
    print("Warning: Rate limit nearly exhausted!")
    # Adjust behavior accordingly
```

### 4. Use Retry Logic for Resilience

```python
retry_handler = RetryHandler(
    RetryConfig(max_retries=3, strategy=RetryStrategy.EXPONENTIAL)
)
response = retry_handler.retry_sync(make_request)
```

### 5. Collect Metrics

Track usage patterns:

```python
metrics = MetricsCollector()
# Record all requests
metrics.record_request(endpoint, status_code, status)
# Export periodically
prometheus_metrics = metrics.export_prometheus()
```

## Common Patterns

### Pattern 1: Batch Processing

```python
limiter = RateLimiter(default_limits={'requests_per_minute': 60})

results = []
for item in items:
    response = limiter.request('POST', 'https://api.example.com/process', json=item)
    results.append(response.json())
```

### Pattern 2: Web Scraper

```python
limiter = RateLimiter(storage='sqlite:///scraper.db')

for url in urls:
    response = limiter.request('GET', url)
    html = response.text
    # Process HTML...
```

### Pattern 3: FastAPI Integration

```python
from fastapi import FastAPI
from smartratelimit import RateLimiter

app = FastAPI()
limiter = RateLimiter(storage='redis://localhost:6379/0')

@app.get("/notify")
def notify_user(user_id: str):
    response = limiter.request(
        'POST',
        'https://api.sendgrid.com/v3/mail/send',
        json={'to': user_id, 'message': 'Hello!'}
    )
    return {"status": "sent"}
```

### Pattern 4: Async Batch Processing

```python
import asyncio
import httpx
from smartratelimit import AsyncRateLimiter

async def process_urls(urls):
    async with AsyncRateLimiter() as limiter:
        async with httpx.AsyncClient() as client:
            tasks = [
                limiter.arequest_httpx(client, 'GET', url)
                for url in urls
            ]
            responses = await asyncio.gather(*tasks)
            return [r.json() for r in responses]

results = asyncio.run(process_urls(urls))
```

### Pattern 5: Wrapping Existing Session

```python
import requests
from smartratelimit import RateLimiter

session = requests.Session()
session.headers.update({'Authorization': 'Bearer token'})

limiter = RateLimiter()
limiter.wrap_session(session)

# Now all session requests are rate-limited
response = session.get('https://api.example.com/data')
```

## Troubleshooting

### Issue: Rate limits not detected

**Solution:** Set default limits manually:
```python
limiter = RateLimiter(default_limits={'requests_per_minute': 60})
```

### Issue: Rate limits lost on restart

**Solution:** Use persistent storage:
```python
limiter = RateLimiter(storage='sqlite:///rate_limits.db')
```

### Issue: Multiple workers exceeding limits

**Solution:** Use Redis for shared state:
```python
limiter = RateLimiter(storage='redis://localhost:6379/0')
```

## Next Steps

- Read the [API Reference](API_REFERENCE.md)
- Check out [examples](../examples/)
- See [Contributing Guide](../CONTRIBUTING.md)

