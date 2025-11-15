"""Helper script to test Redis setup and connectivity."""

import sys


def check_redis():
    """Check if Redis is properly set up."""
    print("Checking Redis setup...")
    print("=" * 50)
    
    # Check Python client
    try:
        import redis
        print("✅ Redis Python client is installed")
        print(f"   Version: {redis.__version__}")
    except ImportError:
        print("❌ Redis Python client is NOT installed")
        print("   Install with: pip install redis")
        return False
    
    # Check Redis server connection
    try:
        client = redis.from_url("redis://localhost:6379/0")
        client.ping()
        print("✅ Redis server is running and accessible")
        print("   Connection: redis://localhost:6379/0")
        
        # Test basic operations
        client.set("test_key", "test_value")
        value = client.get("test_key")
        client.delete("test_key")
        print("✅ Redis operations working correctly")
        return True
    except redis.ConnectionError:
        print("❌ Cannot connect to Redis server")
        print("   Make sure Redis is running on localhost:6379")
        print("   Start Redis with: redis-server")
        return False
    except Exception as e:
        print(f"❌ Error connecting to Redis: {e}")
        return False


if __name__ == "__main__":
    success = check_redis()
    print("=" * 50)
    if success:
        print("✅ Redis is ready for testing!")
        sys.exit(0)
    else:
        print("❌ Redis setup incomplete. See instructions above.")
        sys.exit(1)

