# CLI Guide

Complete guide to using the smartratelimit command-line interface.

## Table of Contents

1. [Installation](#installation)
2. [Basic Commands](#basic-commands)
3. [Status Command](#status-command)
4. [Clear Command](#clear-command)
5. [Probe Command](#probe-command)
6. [List Command](#list-command)
7. [Storage Options](#storage-options)
8. [Examples](#examples)

## Installation

The CLI is automatically installed with the package:

```bash
pip install smartratelimit
```

## Basic Commands

### Help

```bash
python -m smartratelimit.cli --help
```

Or if installed as a script:

```bash
smartratelimit --help
```

## Status Command

View rate limit status for an endpoint.

### Basic Usage

```bash
python -m smartratelimit.cli status "https://api.example.com"
```

### With Storage

```bash
python -m smartratelimit.cli --storage "sqlite:///ratelimit.db" status "https://api.example.com"
```

### Example: Check Status After Making Requests

```python
# First, make some requests using the library
from smartratelimit import RateLimiter

limiter = RateLimiter(storage="sqlite:///ratelimit.db")
url = "https://api.agify.io"

# Make requests
for name in ["Michael", "Sarah", "Alex"]:
    limiter.request("GET", url, params={"name": name})

# Then check status via CLI
# python -m smartratelimit.cli --storage "sqlite:///ratelimit.db" status "https://api.agify.io"
```

### Example Output

```
Endpoint: https://api.agify.io
  Limit: 100
  Remaining: 97
  Utilization: 3.0%
  Resets at: 2024-11-15 12:00:00
  Resets in: 3600 seconds
  Exceeded: False
```

## Clear Command

Clear stored rate limit data.

### Clear Specific Endpoint

```bash
python -m smartratelimit.cli clear "https://api.example.com"
```

### Clear All Data

```bash
python -m smartratelimit.cli clear
```

### With Storage

```bash
python -m smartratelimit.cli --storage "sqlite:///ratelimit.db" clear "https://api.example.com"
```

### Example: Clear After Testing

```python
# Make requests
from smartratelimit import RateLimiter

limiter = RateLimiter(storage="sqlite:///ratelimit.db")
limiter.request("GET", "https://api.example.com/data")

# Clear via CLI
# python -m smartratelimit.cli --storage "sqlite:///ratelimit.db" clear "https://api.example.com"
```

## Probe Command

Probe an endpoint to detect rate limits.

### Basic Usage

```bash
python -m smartratelimit.cli probe "https://api.example.com/data"
```

### Example: Probe Free API

```bash
python -m smartratelimit.cli probe "https://api.github.com/users/octocat"
```

### Example: Probe with Storage

```bash
python -m smartratelimit.cli --storage "sqlite:///ratelimit.db" probe "https://api.agify.io?name=Michael"
```

### Example Output

```
Probing https://api.agify.io?name=Michael...

Response Status: 200

Rate Limit Headers:
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 99
  X-RateLimit-Reset: 1234567890

Detected Rate Limit:
  Limit: 100
  Remaining: 99
  Window: 1 day, 0:00:00
```

## List Command

List all tracked endpoints (requires storage backend support).

```bash
python -m smartratelimit.cli list
```

Note: Currently shows a message that listing requires storage backend support. Use `status` with specific endpoints instead.

## Storage Options

### In-Memory (Default)

```bash
python -m smartratelimit.cli status "https://api.example.com"
```

### SQLite

```bash
python -m smartratelimit.cli --storage "sqlite:///ratelimit.db" status "https://api.example.com"
```

### Redis

```bash
python -m smartratelimit.cli --storage "redis://localhost:6379/0" status "https://api.example.com"
```

## Examples

### Example: Complete Workflow

```python
# Step 1: Make requests using the library
from smartratelimit import RateLimiter

limiter = RateLimiter(storage="sqlite:///ratelimit.db")
url = "https://api.agify.io"

for name in ["Michael", "Sarah", "Alex"]:
    response = limiter.request("GET", url, params={"name": name})
    print(f"{name}: Age {response.json()['age']}")
```

```bash
# Step 2: Check status via CLI
python -m smartratelimit.cli --storage "sqlite:///ratelimit.db" status "https://api.agify.io"
```

```bash
# Step 3: Clear data when done
python -m smartratelimit.cli --storage "sqlite:///ratelimit.db" clear "https://api.agify.io"
```

### Example: Monitoring Rate Limits

```python
# Application code
from smartratelimit import RateLimiter

limiter = RateLimiter(storage="sqlite:///ratelimit.db")

# Make requests throughout the day
# ... your application code ...
```

```bash
# Monitor via CLI (can be run from cron or monitoring system)
python -m smartratelimit.cli --storage "sqlite:///ratelimit.db" status "https://api.example.com"
```

### Example: Testing New Endpoint

```bash
# Probe endpoint to see if it has rate limits
python -m smartratelimit.cli probe "https://api.example.com/data"
```

### Example: Using with Free APIs

```python
# Store data
from smartratelimit import RateLimiter

limiter = RateLimiter(storage="sqlite:///free_apis.db")

# Make requests to free APIs
apis = [
    "https://randomuser.me/api/",
    "https://dog.ceo/api/breeds/image/random",
    "https://api.agify.io"
]

for api in apis:
    if "agify" in api:
        limiter.request("GET", api, params={"name": "Test"})
    else:
        limiter.request("GET", api)
```

```bash
# Check status for each
python -m smartratelimit.cli --storage "sqlite:///free_apis.db" status "https://randomuser.me/api/"
python -m smartratelimit.cli --storage "sqlite:///free_apis.db" status "https://dog.ceo/api/breeds/image/random"
python -m smartratelimit.cli --storage "sqlite:///free_apis.db" status "https://api.agify.io"
```

## More Resources

- 📖 [Quick Start Guide](QUICK_START.md)
- 📚 [Complete Tutorial](TUTORIAL.md)
- 💾 [Storage Backends](STORAGE_BACKENDS.md)
- 💻 [Examples](EXAMPLES.md)

