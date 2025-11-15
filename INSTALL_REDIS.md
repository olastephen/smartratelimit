# Installing Redis on macOS (Without Homebrew/Docker)

## ✅ Step 1: Python Redis Client - DONE!

The Python Redis client is already installed (version 7.0.1).

## Step 2: Install Redis Server

Since Homebrew and Docker are not available, here are alternative methods:

### Option A: Install Homebrew First (Recommended)

Homebrew is the easiest way to install Redis on macOS:

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Then install Redis
brew install redis

# Start Redis
brew services start redis
```

### Option B: Install Redis from Source

1. **Download Redis:**
   ```bash
   cd ~/Downloads
   wget https://download.redis.io/redis-stable.tar.gz
   tar xvzf redis-stable.tar.gz
   cd redis-stable
   ```

2. **Compile Redis:**
   ```bash
   make
   ```

3. **Install Redis:**
   ```bash
   sudo make install
   ```

4. **Start Redis:**
   ```bash
   redis-server
   ```

### Option C: Use MacPorts (if installed)

```bash
sudo port install redis
sudo port load redis
```

### Option D: Download Pre-built Binary

1. Visit: https://redis.io/download
2. Download the macOS binary
3. Extract and run: `./redis-server`

## Step 3: Verify Installation

After installing Redis, verify it works:

```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# Or test with Python
python3 tests/test_redis_setup.py
```

## Quick Start (Once Redis is Installed)

```bash
# Start Redis server (if not running as service)
redis-server

# In another terminal, verify
redis-cli ping

# Run tests
pytest tests/test_storage_redis.py -v
```

## Current Status

✅ **Python Redis client:** Installed (v7.0.1)  
❌ **Redis server:** Not installed/running

Once you install the Redis server using one of the methods above, the tests will work!

