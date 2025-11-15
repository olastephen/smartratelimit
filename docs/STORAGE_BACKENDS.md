# Storage Backends Guide

Complete guide to using different storage backends with smartratelimit.

## Table of Contents

1. [In-Memory Storage](#in-memory-storage)
2. [SQLite Storage](#sqlite-storage)
3. [Redis Storage](#redis-storage)
4. [Choosing the Right Backend](#choosing-the-right-backend)
5. [Migration Between Backends](#migration-between-backends)

## In-Memory Storage

**Default storage** - Fast but data is lost when the process ends.

### Basic Usage

```python
from smartratelimit import RateLimiter

# In-memory is the default
limiter = RateLimiter()  # or RateLimiter(storage="memory")

# Make requests
response = limiter.request("GET", "https://api.example.com/data")

# Data is stored in memory (lost when program exits)
```

### When to Use

- ✅ Development and testing
- ✅ Single-process applications
- ✅ Temporary rate limit tracking
- ✅ When persistence isn't needed

### Example: Quick Testing

```python
from smartratelimit import RateLimiter

limiter = RateLimiter()  # In-memory

# Test with free API
url = "https://api.agify.io"
names = ["Alice", "Bob", "Charlie"]

for name in names:
    response = limiter.request("GET", url, params={"name": name})
    data = response.json()
    print(f"{name}: Age {data['age']}")
    
    # Check status (stored in memory)
    status = limiter.get_status(url)
    if status:
        print(f"  Rate limit: {status.remaining}/{status.limit}\n")
```

## SQLite Storage

**Persistent storage** - Data survives application restarts, perfect for single-machine deployments.

### Basic Usage

```python
from smartratelimit import RateLimiter

# Use SQLite database
limiter = RateLimiter(storage="sqlite:///ratelimit.db")

# Make requests - data persists to database
response = limiter.request("GET", "https://api.example.com/data")
```

### File Path Examples

```python
# Absolute path
limiter = RateLimiter(storage="sqlite:////absolute/path/to/ratelimit.db")

# Relative path
limiter = RateLimiter(storage="sqlite:///ratelimit.db")  # Creates in current directory

# In-memory SQLite (for testing)
limiter = RateLimiter(storage="sqlite:///:memory:")
```

### Example: Persistent Rate Limit Tracking

```python
from smartratelimit import RateLimiter
import os

# Use persistent SQLite storage
db_path = "ratelimit.db"
limiter = RateLimiter(storage=f"sqlite:///{db_path}")

# Make requests - data is saved
url = "https://api.agify.io"
response = limiter.request("GET", url, params={"name": "Michael"})

# Check status
status = limiter.get_status(url)
if status:
    print(f"Rate limit: {status.remaining}/{status.limit}")
    print(f"Data saved to: {db_path}")

# Even if you restart the program, the rate limit data persists!
```

### Example: Multiple Applications Sharing Data

```python
# Application 1
from smartratelimit import RateLimiter

limiter1 = RateLimiter(storage="sqlite:///shared_ratelimit.db")
response = limiter1.request("GET", "https://api.example.com/data")
print("App 1: Request made")

# Application 2 (can be a different process)
from smartratelimit import RateLimiter

limiter2 = RateLimiter(storage="sqlite:///shared_ratelimit.db")
status = limiter2.get_status("https://api.example.com")
print(f"App 2: Rate limit status: {status.remaining}/{status.limit}")
```

### Example: CLI with SQLite

```python
from smartratelimit import RateLimiter

# Store data in SQLite
limiter = RateLimiter(storage="sqlite:///ratelimit.db")

# Make requests
url = "https://api.agify.io"
response = limiter.request("GET", url, params={"name": "Sarah"})

# Later, use CLI to check status
# python -m smartratelimit.cli --storage "sqlite:///ratelimit.db" status "https://api.agify.io"
```

### Managing SQLite Database

```python
from smartratelimit import RateLimiter

limiter = RateLimiter(storage="sqlite:///ratelimit.db")

# Clear all data
limiter.clear()

# Clear specific endpoint
limiter.clear("https://api.example.com")

# Check if database exists
import os
if os.path.exists("ratelimit.db"):
    print("Database exists")
```

## Redis Storage

**Distributed storage** - Share rate limits across multiple processes and machines.

### Prerequisites

Install Redis server and Python client:

```bash
# Install Redis (macOS)
brew install redis
brew services start redis

# Install Python client
pip install redis

# Or install with smartratelimit
pip install smartratelimit[redis]
```

See [REDIS_SETUP.md](../REDIS_SETUP.md) for detailed setup instructions.

### Basic Usage

```python
from smartratelimit import RateLimiter

# Connect to Redis
limiter = RateLimiter(storage="redis://localhost:6379/0")

# Make requests - data stored in Redis
response = limiter.request("GET", "https://api.example.com/data")
```

### Connection String Formats

```python
# Default (localhost, port 6379, database 0)
limiter = RateLimiter(storage="redis://localhost:6379/0")

# With password
limiter = RateLimiter(storage="redis://:password@localhost:6379/0")

# Remote Redis
limiter = RateLimiter(storage="redis://redis.example.com:6379/0")

# With username and password
limiter = RateLimiter(storage="redis://username:password@localhost:6379/0")
```

### Example: Multi-Process Rate Limiting

```python
# Process 1
from smartratelimit import RateLimiter

limiter1 = RateLimiter(storage="redis://localhost:6379/0")
response = limiter1.request("GET", "https://api.example.com/data")
print("Process 1: Request made")

# Process 2 (different process, same machine or different machine)
from smartratelimit import RateLimiter

limiter2 = RateLimiter(storage="redis://localhost:6379/0")
status = limiter2.get_status("https://api.example.com")
print(f"Process 2: Rate limit: {status.remaining}/{status.limit}")
# Both processes share the same rate limit!
```

### Example: Distributed Application

```python
# Server 1
from smartratelimit import RateLimiter

limiter = RateLimiter(storage="redis://redis-server:6379/0")
response = limiter.request("GET", "https://api.example.com/data")

# Server 2 (different server, same Redis instance)
from smartratelimit import RateLimiter

limiter = RateLimiter(storage="redis://redis-server:6379/0")
# Automatically sees the rate limit from Server 1!
```

### Example: Using with Free APIs

```python
from smartratelimit import RateLimiter

# Use Redis for distributed rate limiting
limiter = RateLimiter(storage="redis://localhost:6379/0")

# Multiple workers can share rate limits
url = "https://api.agify.io"
names = ["Alice", "Bob", "Charlie", "David", "Eve"]

for name in names:
    response = limiter.request("GET", url, params={"name": name})
    data = response.json()
    print(f"{name}: Age {data['age']}")
    
    # All workers see the same rate limit status
    status = limiter.get_status(url)
    if status:
        print(f"  Shared rate limit: {status.remaining}/{status.limit}\n")
```

### Redis Key Prefix

```python
from smartratelimit.storage import RedisStorage

# Custom key prefix (default is "ratelimit:")
storage = RedisStorage(
    redis_url="redis://localhost:6379/0",
    key_prefix="myapp:ratelimit:"
)

from smartratelimit import RateLimiter
limiter = RateLimiter(storage=storage)
```

### Checking Redis Connection

```python
from smartratelimit.storage import RedisStorage

try:
    storage = RedisStorage("redis://localhost:6379/0")
    print("✓ Redis connected successfully")
except Exception as e:
    print(f"✗ Redis connection failed: {e}")
```

## Choosing the Right Backend

### Comparison Table

| Feature | In-Memory | SQLite | Redis |
|---------|-----------|--------|-------|
| **Persistence** | ❌ No | ✅ Yes | ✅ Yes |
| **Multi-Process** | ❌ No | ⚠️ Limited | ✅ Yes |
| **Multi-Machine** | ❌ No | ❌ No | ✅ Yes |
| **Speed** | ⚡ Fastest | ⚡ Fast | ⚡ Fast |
| **Setup** | ✅ None | ✅ None | ⚠️ Requires Redis |
| **Best For** | Testing, single process | Single machine, persistence | Distributed systems |

### Decision Guide

**Use In-Memory when:**
- Developing or testing
- Single-process application
- Data persistence not needed
- Maximum performance needed

**Use SQLite when:**
- Single-machine deployment
- Need persistence across restarts
- Simple setup (no external services)
- Multiple processes on same machine (with caution)

**Use Redis when:**
- Multiple processes or machines
- Distributed application
- Need real-time shared state
- Already using Redis infrastructure

## Migration Between Backends

### Export from One Backend

```python
from smartratelimit import RateLimiter

# Read from SQLite
limiter_sqlite = RateLimiter(storage="sqlite:///old.db")

# Get all endpoints (you'd need to implement this)
# For now, manually specify endpoints you want to migrate
endpoints = ["https://api.example.com"]

# Export data
data = {}
for endpoint in endpoints:
    status = limiter_sqlite.get_status(endpoint)
    if status:
        data[endpoint] = status
```

### Import to Another Backend

```python
from smartratelimit import RateLimiter

# Write to Redis
limiter_redis = RateLimiter(storage="redis://localhost:6379/0")

# Set limits manually
for endpoint, status in data.items():
    limiter_redis.set_limit(
        endpoint,
        limit=status.limit,
        window=f"{status.window.total_seconds()}s"
    )
```

## Advanced Examples

### Custom Storage Backend

```python
from smartratelimit.storage import StorageBackend
from smartratelimit.models import RateLimit, TokenBucket

class CustomStorage(StorageBackend):
    def get_rate_limit(self, endpoint: str):
        # Your implementation
        pass
    
    def set_rate_limit(self, endpoint: str, rate_limit: RateLimit):
        # Your implementation
        pass
    
    # Implement other required methods...

# Use custom storage
from smartratelimit import RateLimiter
limiter = RateLimiter(storage=CustomStorage())
```

## More Resources

- 📖 [Quick Start Guide](QUICK_START.md)
- 📚 [Complete Tutorial](TUTORIAL.md)
- 🔧 [Redis Setup Guide](../REDIS_SETUP.md)
- 💻 [Examples](EXAMPLES.md)

