"""Examples demonstrating v0.2.0 features: SQLite and Redis storage."""

from smartratelimit import RateLimiter


def example_sqlite_persistence():
    """Example: Using SQLite for persistent rate limit storage."""
    print("=== SQLite Persistence Example ===")
    
    # Create limiter with SQLite storage
    limiter = RateLimiter(storage='sqlite:///rate_limits.db')
    
    # Set a rate limit
    limiter.set_limit('api.example.com', limit=100, window='1h')
    
    # Check status
    status = limiter.get_status('api.example.com')
    if status:
        print(f"Rate limit: {status.limit} requests per hour")
        print(f"Remaining: {status.remaining}")
    
    # Rate limit state persists across application restarts
    print("Rate limit state saved to rate_limits.db")
    print()


def example_redis_distributed():
    """Example: Using Redis for distributed rate limiting."""
    print("=== Redis Distributed Example ===")
    
    try:
        # Create limiter with Redis storage
        limiter = RateLimiter(storage='redis://localhost:6379/0')
        
        # Set a rate limit (shared across all processes)
        limiter.set_limit('api.example.com', limit=1000, window='1h')
        
        # Check status
        status = limiter.get_status('api.example.com')
        if status:
            print(f"Shared rate limit: {status.limit} requests per hour")
            print("This limit is shared across all processes using this Redis instance")
        
        print("Perfect for Gunicorn workers, Celery tasks, etc.")
    except Exception as e:
        print(f"Redis not available: {e}")
        print("To use Redis, install it with: pip install redis")
        print("And make sure Redis server is running")
    print()


def example_multi_process_scenario():
    """Example: Multi-process scenario with Redis."""
    print("=== Multi-Process Scenario ===")
    print("""
    In a production environment with multiple workers:
    
    # Worker 1, 2, 3, 4... all use the same Redis instance
    limiter = RateLimiter(storage='redis://localhost:6379/0')
    
    # All workers share the same rate limit counter
    # If the API allows 1000 requests/hour, all workers together
    # will respect this limit, not each worker individually
    """)
    print()


if __name__ == "__main__":
    example_sqlite_persistence()
    example_redis_distributed()
    example_multi_process_scenario()
    
    print("v0.2.0 Features Summary:")
    print("✅ SQLite persistence - Rate limits survive app restarts")
    print("✅ Redis distributed - Share limits across processes")
    print("✅ Multi-process safe - Perfect for production deployments")

