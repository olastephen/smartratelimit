# Redis Setup Guide for Testing

This guide will help you set up Redis so that the Redis storage tests can run.

## Quick Setup

### Option 1: Install Redis with Homebrew (macOS)

```bash
# Install Redis
brew install redis

# Start Redis server
brew services start redis

# Or run Redis in foreground (for testing)
redis-server
```

### Option 2: Install Redis with Docker

```bash
# Run Redis in Docker container
docker run -d -p 6379:6379 --name redis-test redis:latest

# Stop Redis when done
docker stop redis-test
docker rm redis-test
```

### Option 3: Install Redis from Source (Linux)

```bash
# Download and compile Redis
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make

# Start Redis server
src/redis-server
```

### Option 4: Use Redis Cloud (Free Tier)

1. Sign up at https://redis.com/try-free/
2. Create a free database
3. Get connection URL
4. Update tests to use your Redis URL

## Install Python Redis Client

```bash
pip install redis
```

Or install with the package:

```bash
pip install smartratelimit[redis]
```

## Verify Redis Setup

Run the setup checker:

```bash
python3 tests/test_redis_setup.py
```

This will check:
- ✅ Redis Python client installation
- ✅ Redis server connectivity
- ✅ Basic Redis operations

## Running Redis Tests

Once Redis is set up, run the Redis tests:

```bash
# Run all Redis tests
pytest tests/test_storage_redis.py -v

# Run all tests (Redis tests will now pass)
pytest tests/ -v
```

## Troubleshooting

### Redis not starting

**macOS:**
```bash
# Check if Redis is already running
redis-cli ping

# If it says "PONG", Redis is running
# If it says "Connection refused", start Redis:
brew services start redis
```

**Linux:**
```bash
# Check Redis status
sudo systemctl status redis

# Start Redis
sudo systemctl start redis
```

### Connection refused error

1. Check if Redis is running:
   ```bash
   redis-cli ping
   ```

2. Check if Redis is listening on port 6379:
   ```bash
   # macOS/Linux
   lsof -i :6379
   
   # Or
   netstat -an | grep 6379
   ```

3. If Redis is not running, start it:
   ```bash
   redis-server
   ```

### Permission denied

If you get permission errors:

```bash
# macOS - Redis should run as your user
# Linux - may need to run as redis user
sudo -u redis redis-server
```

### Using a different Redis URL

If your Redis is on a different host/port, you can:

1. Set environment variable:
   ```bash
   export REDIS_URL="redis://your-host:6379/0"
   ```

2. Or modify the test file to use your URL

## Test Configuration

The tests use these default settings:
- **Host:** localhost
- **Port:** 6379
- **Database:** 0
- **Key prefix:** `test:ratelimit:`

You can modify these in `tests/test_storage_redis.py` if needed.

## Running Tests Without Redis

If you don't want to set up Redis, the tests will automatically skip:

```bash
pytest tests/test_storage_redis.py -v
# Output: "SKIPPED [1] tests/test_storage_redis.py: Redis not available"
```

This is expected and won't cause test failures.

## Continuous Integration

For CI/CD, you can use Docker:

```yaml
# Example GitHub Actions
services:
  redis:
    image: redis:latest
    ports:
      - 6379:6379
```

Or use a Redis service in your CI platform.

## Next Steps

1. Install Redis (choose one method above)
2. Install Python client: `pip install redis`
3. Verify setup: `python3 tests/test_redis_setup.py`
4. Run tests: `pytest tests/test_storage_redis.py -v`

Once Redis is set up, all Redis storage tests will run automatically!

