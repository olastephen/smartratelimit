"""Examples demonstrating v0.3.0 async features."""

import asyncio

# Example 1: Using httpx with AsyncRateLimiter
async def example_httpx():
    """Example: Using httpx with async rate limiter."""
    print("=== httpx Async Example ===")
    
    try:
        import httpx
        from smartratelimit import AsyncRateLimiter
        
        async with AsyncRateLimiter() as limiter:
            async with httpx.AsyncClient() as client:
                # Make rate-limited requests
                response = await limiter.arequest_httpx(
                    client, 'GET', 'https://api.github.com/users/octocat'
                )
                print(f"Status: {response.status_code}")
                print(f"Response: {response.json()}")
    except ImportError:
        print("httpx not installed. Install with: pip install httpx")
    print()


# Example 2: Using aiohttp with AsyncRateLimiter
async def example_aiohttp():
    """Example: Using aiohttp with async rate limiter."""
    print("=== aiohttp Async Example ===")
    
    try:
        import aiohttp
        from smartratelimit import AsyncRateLimiter
        
        async with AsyncRateLimiter() as limiter:
            async with aiohttp.ClientSession() as session:
                response = await limiter.arequest_aiohttp(
                    session, 'GET', 'https://api.github.com/users/octocat'
                )
                print(f"Status: {response.status_code}")
                data = await response.json()
                print(f"Response: {data}")
    except ImportError:
        print("aiohttp not installed. Install with: pip install aiohttp")
    print()


# Example 3: Multiple async requests
async def example_multiple_requests():
    """Example: Making multiple async requests."""
    print("=== Multiple Async Requests ===")
    
    try:
        import httpx
        from smartratelimit import AsyncRateLimiter
        
        urls = [
            'https://api.github.com/users/octocat',
            'https://api.github.com/users/torvalds',
            'https://api.github.com/users/gaearon',
        ]
        
        async with AsyncRateLimiter() as limiter:
            async with httpx.AsyncClient() as client:
                tasks = [
                    limiter.arequest_httpx(client, 'GET', url)
                    for url in urls
                ]
                responses = await asyncio.gather(*tasks)
                
                for response in responses:
                    print(f"Status: {response.status_code}, URL: {response.url}")
    except ImportError:
        print("httpx not installed. Install with: pip install httpx")
    print()


if __name__ == "__main__":
    asyncio.run(example_httpx())
    asyncio.run(example_aiohttp())
    asyncio.run(example_multiple_requests())

