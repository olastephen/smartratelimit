# Async Guide

Complete guide to using smartratelimit with async/await and async HTTP clients.

## Table of Contents

1. [AsyncRateLimiter Overview](#asyncratelimiter-overview)
2. [httpx Integration](#httpx-integration)
3. [aiohttp Integration](#aiohttp-integration)
4. [Async Context Manager](#async-context-manager)
5. [Async Examples](#async-examples)
6. [Best Practices](#best-practices)

## AsyncRateLimiter Overview

`AsyncRateLimiter` provides async/await support for rate-limited HTTP requests.

### Installation

```bash
pip install smartratelimit[httpx]    # For httpx support
pip install smartratelimit[aiohttp]  # For aiohttp support
pip install smartratelimit[all]      # For all async clients
```

### Basic Import

```python
from smartratelimit import AsyncRateLimiter
```

## httpx Integration

### Basic Usage with httpx

```python
import httpx
from smartratelimit import AsyncRateLimiter

async def main():
    # Create async rate limiter
    limiter = AsyncRateLimiter()
    
    # Create httpx client
    async with httpx.AsyncClient() as client:
        # Make rate-limited request
        response = await limiter.arequest_httpx(
            client,
            "GET",
            "https://api.github.com/users/octocat"
        )
        print(response.json())

# Run
import asyncio
asyncio.run(main())
```

### Example: Multiple Requests with httpx

```python
import httpx
from smartratelimit import AsyncRateLimiter
import asyncio

async def fetch_user_data(username):
    limiter = AsyncRateLimiter()
    
    async with httpx.AsyncClient() as client:
        url = f"https://api.github.com/users/{username}"
        response = await limiter.arequest_httpx(client, "GET", url)
        return response.json()

async def main():
    usernames = ["octocat", "torvalds", "gaearon"]
    
    # Fetch all users concurrently
    tasks = [fetch_user_data(username) for username in usernames]
    results = await asyncio.gather(*tasks)
    
    for username, data in zip(usernames, results):
        print(f"{username}: {data.get('name', 'N/A')}")

asyncio.run(main())
```

### Example: Free APIs with httpx

```python
import httpx
from smartratelimit import AsyncRateLimiter
import asyncio

async def get_random_user():
    limiter = AsyncRateLimiter()
    
    async with httpx.AsyncClient() as client:
        response = await limiter.arequest_httpx(
            client,
            "GET",
            "https://randomuser.me/api/"
        )
        return response.json()

async def get_dog_image():
    limiter = AsyncRateLimiter()
    
    async with httpx.AsyncClient() as client:
        response = await limiter.arequest_httpx(
            client,
            "GET",
            "https://dog.ceo/api/breeds/image/random"
        )
        return response.json()

async def get_joke():
    limiter = AsyncRateLimiter()
    
    async with httpx.AsyncClient() as client:
        response = await limiter.arequest_httpx(
            client,
            "GET",
            "https://official-joke-api.appspot.com/random_joke"
        )
        return response.json()

async def main():
    # Fetch all concurrently
    user, dog, joke = await asyncio.gather(
        get_random_user(),
        get_dog_image(),
        get_joke()
    )
    
    print(f"User: {user['results'][0]['name']['first']}")
    print(f"Dog: {dog['message']}")
    print(f"Joke: {joke['setup']} - {joke['punchline']}")

asyncio.run(main())
```

### Example: Batch Processing with httpx

```python
import httpx
from smartratelimit import AsyncRateLimiter
import asyncio

async def analyze_name(name):
    limiter = AsyncRateLimiter()
    
    async with httpx.AsyncClient() as client:
        # Age prediction
        age_response = await limiter.arequest_httpx(
            client,
            "GET",
            "https://api.agify.io",
            params={"name": name}
        )
        
        # Gender prediction
        gender_response = await limiter.arequest_httpx(
            client,
            "GET",
            "https://api.genderize.io",
            params={"name": name}
        )
        
        return {
            "name": name,
            "age": age_response.json().get("age"),
            "gender": gender_response.json().get("gender")
        }

async def main():
    names = ["Michael", "Sarah", "Alex", "Emma", "David"]
    
    # Process all names concurrently
    results = await asyncio.gather(*[analyze_name(name) for name in names])
    
    for result in results:
        print(f"{result['name']}: Age {result['age']}, Gender {result['gender']}")

asyncio.run(main())
```

## aiohttp Integration

### Basic Usage with aiohttp

```python
import aiohttp
from smartratelimit import AsyncRateLimiter
import asyncio

async def main():
    limiter = AsyncRateLimiter()
    
    async with aiohttp.ClientSession() as session:
        response = await limiter.arequest_aiohttp(
            session,
            "GET",
            "https://api.github.com/users/octocat"
        )
        data = await response.json()
        print(data)

asyncio.run(main())
```

### Example: Multiple Requests with aiohttp

```python
import aiohttp
from smartratelimit import AsyncRateLimiter
import asyncio

async def fetch_data(url):
    limiter = AsyncRateLimiter()
    
    async with aiohttp.ClientSession() as session:
        response = await limiter.arequest_aiohttp(session, "GET", url)
        return await response.json()

async def main():
    urls = [
        "https://randomuser.me/api/",
        "https://dog.ceo/api/breeds/image/random",
        "https://official-joke-api.appspot.com/random_joke"
    ]
    
    # Fetch all concurrently
    results = await asyncio.gather(*[fetch_data(url) for url in urls])
    
    for url, data in zip(urls, results):
        print(f"{url}: {data}")

asyncio.run(main())
```

### Example: POST Requests with aiohttp

```python
import aiohttp
from smartratelimit import AsyncRateLimiter
import asyncio

async def validate_email(email):
    limiter = AsyncRateLimiter()
    
    # RapidAPI email validation (template)
    url = "https://phone-and-email-validation-api.p.rapidapi.com/validate-email"
    headers = {
        "x-rapidapi-key": "YOUR_API_KEY",
        "x-rapidapi-host": "phone-and-email-validation-api.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    payload = {"email": email}
    
    async with aiohttp.ClientSession() as session:
        response = await limiter.arequest_aiohttp(
            session,
            "POST",
            url,
            headers=headers,
            json=payload
        )
        return await response.json()

async def main():
    emails = ["info@example.com", "contact@example.com", "test@example.com"]
    
    results = await asyncio.gather(*[validate_email(email) for email in emails])
    
    for email, data in zip(emails, results):
        print(f"{email}: Valid = {data.get('is_valid', False)}")

asyncio.run(main())
```

## Async Context Manager

### Using AsyncRateLimiter as Context Manager

```python
import httpx
from smartratelimit import AsyncRateLimiter
import asyncio

async def main():
    async with AsyncRateLimiter() as limiter:
        async with httpx.AsyncClient() as client:
            response = await limiter.arequest_httpx(
                client,
                "GET",
                "https://api.example.com/data"
            )
            print(response.json())

asyncio.run(main())
```

## Async Examples

### Example: Weather API (OpenWeatherMap Template)

```python
import httpx
from smartratelimit import AsyncRateLimiter
import asyncio

async def get_weather(city, country, api_key):
    limiter = AsyncRateLimiter()
    
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": f"{city},{country}",
        "appid": api_key,
        "units": "metric"
    }
    
    async with httpx.AsyncClient() as client:
        response = await limiter.arequest_httpx(client, "GET", url, params=params)
        return response.json()

async def main():
    API_KEY = "YOUR_API_KEY"
    
    cities = [
        ("London", "GB"),
        ("New York", "US"),
        ("Tokyo", "JP")
    ]
    
    # Fetch all weather data concurrently
    tasks = [get_weather(city, country, API_KEY) for city, country in cities]
    results = await asyncio.gather(*tasks)
    
    for (city, country), data in zip(cities, results):
        print(f"{city}: {data['main']['temp']}°C - {data['weather'][0]['description']}")

asyncio.run(main())
```

### Example: Rate Limit Status in Async

```python
import httpx
from smartratelimit import AsyncRateLimiter
import asyncio

async def make_request_and_check_status():
    limiter = AsyncRateLimiter()
    url = "https://api.agify.io"
    
    async with httpx.AsyncClient() as client:
        response = await limiter.arequest_httpx(
            client,
            "GET",
            url,
            params={"name": "Michael"}
        )
        
        # Check rate limit status
        status = limiter.get_status(url)
        if status:
            print(f"Rate limit: {status.remaining}/{status.limit} remaining")
        
        return response.json()

asyncio.run(make_request_and_check_status())
```

### Example: Error Handling in Async

```python
import httpx
from smartratelimit import AsyncRateLimiter
import asyncio

async def safe_request(url, max_retries=3):
    limiter = AsyncRateLimiter()
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await limiter.arequest_httpx(client, "GET", url)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    print(f"Rate limit exceeded. Retry {attempt + 1}/{max_retries}")
                    await asyncio.sleep(5)
                    continue
                else:
                    print(f"Error {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"Error: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
                continue
    
    return None

async def main():
    data = await safe_request("https://api.example.com/data")
    if data:
        print("Success:", data)

asyncio.run(main())
```

## Best Practices

### 1. Reuse Rate Limiter Instance

```python
# Good: Reuse limiter
async def process_multiple():
    limiter = AsyncRateLimiter()
    async with httpx.AsyncClient() as client:
        for url in urls:
            await limiter.arequest_httpx(client, "GET", url)

# Avoid: Creating new limiter for each request
async def process_multiple_bad():
    async with httpx.AsyncClient() as client:
        for url in urls:
            limiter = AsyncRateLimiter()  # Don't do this!
            await limiter.arequest_httpx(client, "GET", url)
```

### 2. Use Context Managers

```python
# Good: Use context managers
async with AsyncRateLimiter() as limiter:
    async with httpx.AsyncClient() as client:
        # Make requests
        pass
```

### 3. Handle Rate Limits Gracefully

```python
async def make_request_with_retry():
    limiter = AsyncRateLimiter()
    
    async with httpx.AsyncClient() as client:
        try:
            response = await limiter.arequest_httpx(client, "GET", url)
            return response
        except Exception as e:
            # Handle errors
            status = limiter.get_status(url)
            if status and status.is_exceeded:
                print(f"Rate limit exceeded. Wait {status.reset_in:.0f} seconds")
            raise
```

## More Resources

- 📖 [Quick Start Guide](QUICK_START.md)
- 📚 [Complete Tutorial](TUTORIAL.md)
- 💻 [Examples](EXAMPLES.md)
- 📊 [API Reference](API_REFERENCE.md)

