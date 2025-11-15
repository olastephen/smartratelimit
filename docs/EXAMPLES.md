# Comprehensive Examples

Real-world examples using various free APIs and services.

## Table of Contents

1. [Free APIs (No Key Required)](#free-apis-no-key-required)
2. [RapidAPI Examples](#rapidapi-examples)
3. [OpenWeatherMap Examples](#openweathermap-examples)
4. [Batch Processing](#batch-processing)
5. [Error Handling](#error-handling)
6. [Advanced Patterns](#advanced-patterns)

## Free APIs (No Key Required)

### Random User Generator

```python
from smartratelimit import RateLimiter

limiter = RateLimiter()

# Get multiple random users
for i in range(5):
    response = limiter.request("GET", "https://randomuser.me/api/")
    user = response.json()["results"][0]
    
    print(f"User {i+1}:")
    print(f"  Name: {user['name']['first']} {user['name']['last']}")
    print(f"  Email: {user['email']}")
    print(f"  Phone: {user['phone']}")
    print(f"  Location: {user['location']['city']}, {user['location']['country']}")
    print()
```

### Dog Images Collection

```python
from smartratelimit import RateLimiter

limiter = RateLimiter()

# Collect random dog images
dog_images = []
for _ in range(10):
    response = limiter.request("GET", "https://dog.ceo/api/breeds/image/random")
    data = response.json()
    dog_images.append(data['message'])
    print(f"Collected: {data['message']}")

print(f"\nTotal images collected: {len(dog_images)}")
```

### Joke Generator

```python
from smartratelimit import RateLimiter

limiter = RateLimiter()

# Get programming jokes
url = "https://official-joke-api.appspot.com/jokes/programming/random"

for _ in range(5):
    response = limiter.request("GET", url)
    joke = response.json()[0]
    print(f"Q: {joke['setup']}")
    print(f"A: {joke['punchline']}\n")
```

### IP Geolocation

```python
from smartratelimit import RateLimiter

limiter = RateLimiter()

# Get your IP
response = limiter.request("GET", "https://api.ipify.org?format=json")
ip_data = response.json()
ip = ip_data['ip']

print(f"Your IP: {ip}")

# Get IP info (if available)
# Note: ipinfo.io requires API key for full access, but basic info works
try:
    response = limiter.request("GET", f"https://ipinfo.io/{ip}/json")
    info = response.json()
    print(f"Location: {info.get('city', 'N/A')}, {info.get('country', 'N/A')}")
    print(f"ISP: {info.get('org', 'N/A')}")
except:
    print("IP info not available without API key")
```

### Name Analysis (Multiple APIs)

```python
from smartratelimit import RateLimiter

limiter = RateLimiter()

def analyze_name(name):
    """Analyze a name using multiple APIs."""
    results = {}
    
    # Age prediction
    response = limiter.request("GET", "https://api.agify.io", params={"name": name})
    results['age'] = response.json().get('age')
    
    # Gender prediction
    response = limiter.request("GET", "https://api.genderize.io", params={"name": name})
    results['gender'] = response.json().get('gender')
    results['gender_probability'] = response.json().get('probability', 0) * 100
    
    # Nationality prediction
    response = limiter.request("GET", "https://api.nationalize.io", params={"name": name})
    countries = response.json().get('country', [])
    if countries:
        results['nationality'] = countries[0]['country_id']
        results['nationality_probability'] = countries[0]['probability'] * 100
    
    return results

# Analyze multiple names
names = ["Michael", "Sarah", "Alex", "Emma"]
for name in names:
    analysis = analyze_name(name)
    print(f"\n{name}:")
    print(f"  Predicted Age: {analysis.get('age', 'N/A')}")
    print(f"  Gender: {analysis.get('gender', 'N/A')} ({analysis.get('gender_probability', 0):.1f}%)")
    print(f"  Nationality: {analysis.get('nationality', 'N/A')} ({analysis.get('nationality_probability', 0):.1f}%)")
```

## RapidAPI Examples

### Phone Validation (Template)

```python
from smartratelimit import RateLimiter

limiter = RateLimiter()

# RapidAPI phone validation endpoint
# Replace YOUR_API_KEY with your actual RapidAPI key
url = "https://phone-and-email-validation-api.p.rapidapi.com/validate-phone"
headers = {
    "x-rapidapi-key": "YOUR_API_KEY",  # Get from https://rapidapi.com
    "x-rapidapi-host": "phone-and-email-validation-api.p.rapidapi.com",
    "Content-Type": "application/json"
}

# Validate phone number
payload = {"phone_number": "+12065550100"}

response = limiter.request("POST", url, headers=headers, json=payload)

if response.status_code == 200:
    data = response.json()
    print(f"Phone: {data.get('format_e164', 'N/A')}")
    print(f"Valid: {data.get('is_valid', False)}")
    print(f"Country: {data.get('country', 'N/A')}")
    print(f"Location: {data.get('location', 'N/A')}")
    
    # Check rate limit (RapidAPI returns rate limit headers!)
    status = limiter.get_status(url)
    if status:
        print(f"\nRate Limit: {status.remaining}/{status.limit} remaining")
```

### Email Validation (Template)

```python
from smartratelimit import RateLimiter

limiter = RateLimiter()

# RapidAPI email validation
url = "https://phone-and-email-validation-api.p.rapidapi.com/validate-email"
headers = {
    "x-rapidapi-key": "YOUR_API_KEY",  # Get from https://rapidapi.com
    "x-rapidapi-host": "phone-and-email-validation-api.p.rapidapi.com",
    "Content-Type": "application/json"
}

# Validate email
emails = [
    "info@facebook.com",
    "contact@google.com",
    "invalid-email"
]

for email in emails:
    payload = {"email": email}
    response = limiter.request("POST", url, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"{email}:")
        print(f"  Valid: {data.get('is_valid', False)}")
        print(f"  Domain: {data.get('metadata', {}).get('domain', 'N/A')}")
        print(f"  MX Records: {data.get('metadata', {}).get('mx_records', False)}")
        print()
```

### Batch Phone Validation

```python
from smartratelimit import RateLimiter

limiter = RateLimiter()

url = "https://phone-and-email-validation-api.p.rapidapi.com/validate-phone"
headers = {
    "x-rapidapi-key": "YOUR_API_KEY",
    "x-rapidapi-host": "phone-and-email-validation-api.p.rapidapi.com",
    "Content-Type": "application/json"
}

phone_numbers = [
    "+12065550100",
    "+442071234567",
    "+33123456789"
]

validated = []
for phone in phone_numbers:
    response = limiter.request("POST", url, headers=headers, json={"phone_number": phone})
    
    if response.status_code == 200:
        data = response.json()
        validated.append({
            "phone": phone,
            "valid": data.get("is_valid", False),
            "country": data.get("country", "N/A")
        })
        
        # Monitor rate limit
        status = limiter.get_status(url)
        if status:
            print(f"Validated {phone}: {data.get('is_valid')} | "
                  f"Rate limit: {status.remaining}/{status.limit}")

print(f"\nTotal validated: {len(validated)}")
```

## OpenWeatherMap Examples

### Current Weather (Template)

```python
from smartratelimit import RateLimiter

limiter = RateLimiter()

# OpenWeatherMap API
# Get your free API key from https://openweathermap.org/api
API_KEY = "YOUR_API_KEY"  # Replace with your key
BASE_URL = "https://api.openweathermap.org/data/2.5"

# Get current weather for a city
url = f"{BASE_URL}/weather"
params = {
    "q": "London,GB",
    "appid": API_KEY,
    "units": "metric"  # Use Celsius
}

response = limiter.request("GET", url, params=params)

if response.status_code == 200:
    data = response.json()
    print(f"Weather in {data['name']}, {data['sys']['country']}:")
    print(f"  Temperature: {data['main']['temp']}°C")
    print(f"  Feels like: {data['main']['feels_like']}°C")
    print(f"  Condition: {data['weather'][0]['description']}")
    print(f"  Humidity: {data['main']['humidity']}%")
    print(f"  Wind: {data['wind']['speed']} m/s")
    print(f"  Pressure: {data['main']['pressure']} hPa")
```

### Weather for Multiple Cities

```python
from smartratelimit import RateLimiter

limiter = RateLimiter()

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.openweathermap.org/data/2.5"

cities = [
    ("London", "GB"),
    ("New York", "US"),
    ("Tokyo", "JP"),
    ("Paris", "FR"),
    ("Sydney", "AU")
]

url = f"{BASE_URL}/weather"

for city, country in cities:
    params = {
        "q": f"{city},{country}",
        "appid": API_KEY,
        "units": "metric"
    }
    
    response = limiter.request("GET", url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"{city}: {data['main']['temp']}°C - {data['weather'][0]['description']}")
```

### 5-Day Forecast

```python
from smartratelimit import RateLimiter
from datetime import datetime

limiter = RateLimiter()

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.openweathermap.org/data/2.5"

url = f"{BASE_URL}/forecast"
params = {
    "q": "London,GB",
    "appid": API_KEY,
    "units": "metric"
}

response = limiter.request("GET", url, params=params)

if response.status_code == 200:
    data = response.json()
    print(f"5-Day Forecast for {data['city']['name']}, {data['city']['country']}:\n")
    
    # Show first 5 forecasts
    for item in data['list'][:5]:
        dt = datetime.strptime(item['dt_txt'], "%Y-%m-%d %H:%M:%S")
        print(f"{dt.strftime('%a %b %d, %H:%M')}:")
        print(f"  Temperature: {item['main']['temp']}°C")
        print(f"  Condition: {item['weather'][0]['description']}")
        print(f"  Humidity: {item['main']['humidity']}%")
        print()
```

### Weather by Coordinates

```python
from smartratelimit import RateLimiter

limiter = RateLimiter()

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.openweathermap.org/data/2.5"

# London coordinates
lat, lon = 51.5074, -0.1278

url = f"{BASE_URL}/weather"
params = {
    "lat": lat,
    "lon": lon,
    "appid": API_KEY,
    "units": "metric"
}

response = limiter.request("GET", url, params=params)

if response.status_code == 200:
    data = response.json()
    print(f"Location: {data['name']}, {data['sys']['country']}")
    print(f"Coordinates: {data['coord']['lat']}, {data['coord']['lon']}")
    print(f"Temperature: {data['main']['temp']}°C")
    print(f"Condition: {data['weather'][0]['description']}")
```

## Batch Processing

### Process Multiple Items with Error Handling

```python
from smartratelimit import RateLimiter

limiter = RateLimiter()

def process_item(item):
    """Process a single item with error handling."""
    try:
        # Your API call here
        response = limiter.request("GET", f"https://api.example.com/data/{item}")
        
        if response.status_code == 200:
            return {"item": item, "status": "success", "data": response.json()}
        else:
            return {"item": item, "status": "error", "code": response.status_code}
            
    except Exception as e:
        return {"item": item, "status": "exception", "error": str(e)}

# Process multiple items
items = ["item1", "item2", "item3", "item4", "item5"]
results = []

for item in items:
    result = process_item(item)
    results.append(result)
    
    # Check rate limit status
    status = limiter.get_status("https://api.example.com")
    if status:
        print(f"Processed {item}: {result['status']} | "
              f"Rate limit: {status.remaining}/{status.limit}")

# Summary
successful = sum(1 for r in results if r['status'] == 'success')
print(f"\nProcessed {len(results)} items: {successful} successful")
```

## Error Handling

### Comprehensive Error Handling

```python
from smartratelimit import RateLimiter, RateLimitExceeded
import time

limiter = RateLimiter(raise_on_limit=True)  # Raise exception instead of waiting

def safe_request(url, max_retries=3):
    """Make a request with retry logic."""
    for attempt in range(max_retries):
        try:
            response = limiter.request("GET", url)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print(f"Rate limit exceeded. Attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(5)  # Wait before retry
                    continue
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None
                
        except RateLimitExceeded as e:
            print(f"Rate limit exceeded: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
                
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    return None

# Usage
data = safe_request("https://api.example.com/data")
if data:
    print("Success:", data)
```

## Advanced Patterns

### Context Manager Pattern

```python
from smartratelimit import RateLimiter

# Use as context manager for automatic cleanup
with RateLimiter() as limiter:
    response = limiter.request("GET", "https://api.example.com/data")
    print(response.json())
```

### Session Wrapping

```python
from smartratelimit import RateLimiter
import requests

limiter = RateLimiter()

# Wrap a requests session
session = requests.Session()
wrapped_session = limiter.wrap_session(session)

# Use the wrapped session - rate limiting is automatic!
response = wrapped_session.get("https://api.example.com/data")
print(response.json())
```

### Custom Headers Mapping

```python
from smartratelimit import RateLimiter

# For APIs with custom rate limit header names
limiter = RateLimiter(
    headers_map={
        "limit": "X-MyAPI-Limit",
        "remaining": "X-MyAPI-Remaining",
        "reset": "X-MyAPI-Reset"
    }
)

response = limiter.request("GET", "https://api.example.com/data")
```

### Default Limits Fallback

```python
from smartratelimit import RateLimiter

# Set default limits for APIs without rate limit headers
limiter = RateLimiter(
    default_limits={
        "requests_per_minute": 60,
        "requests_per_hour": 1000
    }
)

# These limits will be used if API doesn't provide headers
response = limiter.request("GET", "https://api.example.com/data")
```

## More Examples

- 📖 [Quick Start Guide](QUICK_START.md) - Get started in 5 minutes
- 📚 [Complete Tutorial](TUTORIAL.md) - Step-by-step guide
- 💾 [Storage Backends](STORAGE_BACKENDS.md) - SQLite and Redis examples
- ⚡ [Async Guide](ASYNC_GUIDE.md) - Async/await examples
- 🔄 [Retry Strategies](RETRY_STRATEGIES.md) - Retry logic examples

