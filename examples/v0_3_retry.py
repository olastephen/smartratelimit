"""Examples demonstrating v0.3.0 retry features."""

from smartratelimit import RateLimiter
from smartratelimit.retry import RetryConfig, RetryHandler, RetryStrategy


def example_retry_exponential():
    """Example: Using exponential backoff retry."""
    print("=== Exponential Backoff Retry ===")
    
    retry_config = RetryConfig(
        max_retries=3,
        strategy=RetryStrategy.EXPONENTIAL,
        base_delay=1.0,
        backoff_factor=2.0,
    )
    
    retry_handler = RetryHandler(retry_config)
    limiter = RateLimiter()
    
    def make_request():
        return limiter.request('GET', 'https://api.example.com/data')
    
    try:
        response = retry_handler.retry_sync(make_request)
        print(f"Success: {response.status_code}")
    except Exception as e:
        print(f"Failed after retries: {e}")
    print()


def example_retry_linear():
    """Example: Using linear backoff retry."""
    print("=== Linear Backoff Retry ===")
    
    retry_config = RetryConfig(
        max_retries=5,
        strategy=RetryStrategy.LINEAR,
        base_delay=2.0,
        max_delay=10.0,
    )
    
    retry_handler = RetryHandler(retry_config)
    limiter = RateLimiter()
    
    def make_request():
        return limiter.request('GET', 'https://api.example.com/data')
    
    try:
        response = retry_handler.retry_sync(make_request)
        print(f"Success: {response.status_code}")
    except Exception as e:
        print(f"Failed after retries: {e}")
    print()


def example_retry_custom_status():
    """Example: Retry on custom status codes."""
    print("=== Custom Status Code Retry ===")
    
    retry_config = RetryConfig(
        max_retries=3,
        strategy=RetryStrategy.EXPONENTIAL,
        retry_on_status=[429, 503, 504, 502],  # Include 502 Bad Gateway
    )
    
    retry_handler = RetryHandler(retry_config)
    limiter = RateLimiter()
    
    def make_request():
        return limiter.request('GET', 'https://api.example.com/data')
    
    try:
        response = retry_handler.retry_sync(make_request)
        print(f"Success: {response.status_code}")
    except Exception as e:
        print(f"Failed after retries: {e}")
    print()


if __name__ == "__main__":
    example_retry_exponential()
    example_retry_linear()
    example_retry_custom_status()

