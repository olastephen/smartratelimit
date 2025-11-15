# Advanced Features Guide

Advanced usage patterns and features of smartratelimit.

## Table of Contents

1. [Custom Header Mapping](#custom-header-mapping)
2. [Default Limits](#default-limits)
3. [Exception Handling](#exception-handling)
4. [Session Wrapping](#session-wrapping)
5. [Context Managers](#context-managers)
6. [Multi-Process Patterns](#multi-process-patterns)

## Custom Header Mapping

For APIs with non-standard rate limit header names.

```python
from smartratelimit import RateLimiter

limiter = RateLimiter(
    headers_map={
        "limit": "X-MyAPI-Limit",
        "remaining": "X-MyAPI-Remaining",
        "reset": "X-MyAPI-Reset"
    }
)

response = limiter.request("GET", "https://api.example.com/data")
```

## Default Limits

Set fallback limits when APIs don't provide headers.

```python
from smartratelimit import RateLimiter

limiter = RateLimiter(
    default_limits={
        "requests_per_second": 10,
        "requests_per_minute": 60,
        "requests_per_hour": 1000
    }
)

# These limits apply if API doesn't provide rate limit headers
response = limiter.request("GET", "https://api.example.com/data")
```

## Exception Handling

### Raise on Limit

```python
from smartratelimit import RateLimiter, RateLimitExceeded

limiter = RateLimiter(raise_on_limit=True)

try:
    response = limiter.request("GET", "https://api.example.com/data")
except RateLimitExceeded as e:
    print(f"Rate limit exceeded: {e}")
```

## Session Wrapping

Wrap existing requests sessions.

```python
from smartratelimit import RateLimiter
import requests

limiter = RateLimiter()
session = requests.Session()
wrapped = limiter.wrap_session(session)

# Use wrapped session - rate limiting is automatic
response = wrapped.get("https://api.example.com/data")
```

## Context Managers

```python
from smartratelimit import RateLimiter

with RateLimiter() as limiter:
    response = limiter.request("GET", "https://api.example.com/data")
    print(response.json())
```

## Multi-Process Patterns

### Shared SQLite Database

```python
# Process 1
from smartratelimit import RateLimiter
limiter1 = RateLimiter(storage="sqlite:///shared.db")
limiter1.request("GET", "https://api.example.com/data")

# Process 2 (same database)
limiter2 = RateLimiter(storage="sqlite:///shared.db")
status = limiter2.get_status("https://api.example.com")
```

### Redis for Distributed Systems

```python
# Server 1
from smartratelimit import RateLimiter
limiter1 = RateLimiter(storage="redis://redis-server:6379/0")
limiter1.request("GET", "https://api.example.com/data")

# Server 2 (different server, same Redis)
limiter2 = RateLimiter(storage="redis://redis-server:6379/0")
# Automatically sees rate limit from Server 1
```

## More Resources

- 📖 [Quick Start Guide](QUICK_START.md)
- 📚 [Complete Tutorial](TUTORIAL.md)
- 💻 [Examples](EXAMPLES.md)
- 📊 [API Reference](API_REFERENCE.md)

