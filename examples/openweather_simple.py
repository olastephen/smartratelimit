"""
Simple example: Get weather using OpenWeatherMap API with smartratelimit.

This is a minimal example showing the basic usage.
"""

from smartratelimit import RateLimiter

# Create rate limiter
limiter = RateLimiter()

# Your API key - Get from https://openweathermap.org/api
API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"

# Get current weather for a city
city = "London"
url = "https://api.openweathermap.org/data/2.5/weather"
params = {
    "q": city,
    "appid": API_KEY,
    "units": "metric"  # Use Celsius
}

# Make request - rate limiting is automatic!
response = limiter.request("GET", url, params=params)

# Parse response
if response.status_code == 200:
    data = response.json()
    print(f"Weather in {data['name']}, {data['sys']['country']}:")
    print(f"  Temperature: {data['main']['temp']}°C")
    print(f"  Description: {data['weather'][0]['description']}")
    print(f"  Humidity: {data['main']['humidity']}%")
    print(f"  Wind Speed: {data['wind']['speed']} m/s")
else:
    print(f"Error: {response.status_code}")
    print(response.text)

# Check rate limit status
status = limiter.get_status(url)
if status:
    print(f"\n📊 Rate Limit: {status.remaining}/{status.limit} remaining")

