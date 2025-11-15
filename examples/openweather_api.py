"""
Example: Using smartratelimit with OpenWeatherMap API.

This demonstrates how to integrate smartratelimit with OpenWeatherMap
to automatically handle rate limits.
"""

from smartratelimit import RateLimiter
import json

# Create rate limiter - automatically detects and manages rate limits
limiter = RateLimiter()

# OpenWeatherMap API configuration
# Get your free API key from https://openweathermap.org/api
API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"
BASE_URL = "https://api.openweathermap.org/data/2.5"

# Example 1: Get current weather for a city
def get_current_weather(city_name, country_code=None):
    """Get current weather for a city."""
    if country_code:
        query = f"{city_name},{country_code}"
    else:
        query = city_name
    
    url = f"{BASE_URL}/weather"
    params = {
        "q": query,
        "appid": API_KEY,
        "units": "metric"  # Use metric units (Celsius)
    }
    
    # Make request - rate limiting is automatic!
    response = limiter.request("GET", url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"]
        }
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


# Example 2: Get weather for multiple cities
def get_weather_for_multiple_cities(cities):
    """Get weather for multiple cities with automatic rate limiting."""
    results = []
    
    for city in cities:
        try:
            weather = get_current_weather(city)
            if weather:
                results.append(weather)
                print(f"✓ {weather['city']}, {weather['country']}: {weather['temperature']}°C - {weather['description']}")
            else:
                print(f"✗ Failed to get weather for {city}")
        except Exception as e:
            print(f"✗ Error for {city}: {e}")
        
        # Check rate limit status
        status = limiter.get_status(BASE_URL)
        if status:
            print(f"  Rate limit: {status.remaining}/{status.limit} remaining\n")
    
    return results


# Example 3: Get 5-day forecast
def get_forecast(city_name, country_code=None):
    """Get 5-day weather forecast for a city."""
    if country_code:
        query = f"{city_name},{country_code}"
    else:
        query = city_name
    
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
        for item in data["list"][:5]:  # Get first 5 forecasts
            forecasts.append({
                "datetime": item["dt_txt"],
                "temperature": item["main"]["temp"],
                "description": item["weather"][0]["description"],
                "humidity": item["main"]["humidity"]
            })
        return {
            "city": data["city"]["name"],
            "country": data["city"]["country"],
            "forecasts": forecasts
        }
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


# Example 4: Get weather by coordinates
def get_weather_by_coordinates(lat, lon):
    """Get current weather by latitude and longitude."""
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
        return {
            "location": f"{data['name']}, {data['sys']['country']}",
            "coordinates": f"{data['coord']['lat']}, {data['coord']['lon']}",
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"]
        }
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("OpenWeatherMap API with smartratelimit")
    print("=" * 60)
    
    # Example 1: Get current weather for a single city
    print("\n1. Current Weather for London:")
    print("-" * 60)
    weather = get_current_weather("London", "GB")
    if weather:
        print(f"City: {weather['city']}, {weather['country']}")
        print(f"Temperature: {weather['temperature']}°C")
        print(f"Description: {weather['description']}")
        print(f"Humidity: {weather['humidity']}%")
        print(f"Wind Speed: {weather['wind_speed']} m/s")
    
    # Check rate limit status
    status = limiter.get_status(BASE_URL)
    if status:
        print(f"\n📊 Rate Limit Status:")
        print(f"   Remaining: {status.remaining}/{status.limit}")
        print(f"   Resets in: {status.reset_in:.0f} seconds")
    
    # Example 2: Get weather for multiple cities
    print("\n\n2. Weather for Multiple Cities:")
    print("-" * 60)
    cities = ["New York", "Tokyo", "Paris", "Sydney"]
    results = get_weather_for_multiple_cities(cities)
    
    # Example 3: Get forecast
    print("\n\n3. 5-Day Forecast for London:")
    print("-" * 60)
    forecast = get_forecast("London", "GB")
    if forecast:
        print(f"City: {forecast['city']}, {forecast['country']}")
        print("\nForecast:")
        for f in forecast['forecasts']:
            print(f"  {f['datetime']}: {f['temperature']}°C - {f['description']}")
    
    # Final rate limit status
    print("\n\n" + "=" * 60)
    print("Final Rate Limit Status:")
    print("=" * 60)
    final_status = limiter.get_status(BASE_URL)
    if final_status:
        print(f"Remaining: {final_status.remaining}/{final_status.limit}")
        print(f"Utilization: {final_status.utilization * 100:.1f}%")
        print(f"Resets in: {final_status.reset_in:.0f} seconds")

