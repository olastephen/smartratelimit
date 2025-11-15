"""
Complete example: OpenWeatherMap API with smartratelimit.

This example demonstrates various OpenWeatherMap API endpoints
with automatic rate limiting.
"""

from smartratelimit import RateLimiter
import json
from datetime import datetime

# Initialize rate limiter
limiter = RateLimiter()

# API Configuration
# Get your free API key from https://openweathermap.org/api
API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"
BASE_URL = "https://api.openweathermap.org/data/2.5"


def print_weather(data):
    """Pretty print weather data."""
    print(f"\n📍 {data['name']}, {data['sys']['country']}")
    print(f"   Temperature: {data['main']['temp']}°C (feels like {data['main']['feels_like']}°C)")
    print(f"   Condition: {data['weather'][0]['main']} - {data['weather'][0]['description']}")
    print(f"   Humidity: {data['main']['humidity']}%")
    print(f"   Pressure: {data['main']['pressure']} hPa")
    print(f"   Wind: {data['wind']['speed']} m/s")
    if 'visibility' in data:
        print(f"   Visibility: {data['visibility']/1000:.1f} km")


def get_weather(city, country_code=None):
    """Get current weather for a city."""
    query = f"{city},{country_code}" if country_code else city
    url = f"{BASE_URL}/weather"
    params = {
        "q": query,
        "appid": API_KEY,
        "units": "metric"
    }
    
    response = limiter.request("GET", url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        return None


def get_forecast(city, country_code=None, days=5):
    """Get weather forecast for a city."""
    query = f"{city},{country_code}" if country_code else city
    url = f"{BASE_URL}/forecast"
    params = {
        "q": query,
        "appid": API_KEY,
        "units": "metric"
    }
    
    response = limiter.request("GET", url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        forecasts = []
        for item in data["list"][:days]:
            forecasts.append({
                "datetime": item["dt_txt"],
                "temp": item["main"]["temp"],
                "description": item["weather"][0]["description"],
                "humidity": item["main"]["humidity"]
            })
        return {
            "city": data["city"]["name"],
            "country": data["city"]["country"],
            "forecasts": forecasts
        }
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        return None


def get_weather_by_coords(lat, lon):
    """Get weather by coordinates."""
    url = f"{BASE_URL}/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"
    }
    
    response = limiter.request("GET", url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        return None


def check_rate_limit():
    """Check and display rate limit status."""
    status = limiter.get_status(BASE_URL)
    if status:
        print(f"\n📊 Rate Limit Status:")
        print(f"   Remaining: {status.remaining}/{status.limit}")
        print(f"   Utilization: {status.utilization * 100:.1f}%")
        if status.reset_in:
            print(f"   Resets in: {status.reset_in:.0f} seconds")
    else:
        print("\n📊 Rate limit information not available (may not be in headers)")


if __name__ == "__main__":
    print("=" * 70)
    print("OpenWeatherMap API with smartratelimit")
    print("=" * 70)
    
    # Example 1: Current weather for a city
    print("\n1️⃣  Current Weather - London, UK")
    print("-" * 70)
    weather = get_weather("London", "GB")
    if weather:
        print_weather(weather)
    
    check_rate_limit()
    
    # Example 2: Weather for multiple cities
    print("\n\n2️⃣  Weather for Multiple Cities")
    print("-" * 70)
    cities = [
        ("New York", "US"),
        ("Tokyo", "JP"),
        ("Paris", "FR"),
        ("Sydney", "AU")
    ]
    
    for city, country in cities:
        weather = get_weather(city, country)
        if weather:
            print(f"✓ {weather['name']}: {weather['main']['temp']}°C - {weather['weather'][0]['description']}")
    
    check_rate_limit()
    
    # Example 3: 5-day forecast
    print("\n\n3️⃣  5-Day Forecast - London, UK")
    print("-" * 70)
    forecast = get_forecast("London", "GB", days=5)
    if forecast:
        print(f"\n📍 {forecast['city']}, {forecast['country']}")
        print("\nForecast:")
        for f in forecast['forecasts']:
            dt = datetime.strptime(f['datetime'], "%Y-%m-%d %H:%M:%S")
            print(f"  {dt.strftime('%a %b %d, %H:%M')}: {f['temp']}°C - {f['description']}")
    
    check_rate_limit()
    
    # Example 4: Weather by coordinates (London coordinates)
    print("\n\n4️⃣  Weather by Coordinates (London)")
    print("-" * 70)
    # London coordinates: 51.5074° N, 0.1278° W
    weather = get_weather_by_coords(51.5074, -0.1278)
    if weather:
        print_weather(weather)
    
    check_rate_limit()
    
    print("\n" + "=" * 70)
    print("✅ All requests completed successfully!")
    print("=" * 70)

