"""
Working Free APIs Demo: Testing smartratelimit with reliable free APIs.

This focuses on APIs that are currently working and demonstrate
rate limit detection capabilities.
"""

from smartratelimit import RateLimiter
import json

# Create rate limiter
limiter = RateLimiter()

print("=" * 70)
print("Testing smartratelimit with Working Free APIs")
print("=" * 70)


# APIs that work and show rate limit detection
working_apis = [
    {
        "name": "Dog Images",
        "url": "https://dog.ceo/api/breeds/image/random",
        "description": "Get random dog images"
    },
    {
        "name": "Random User",
        "url": "https://randomuser.me/api/",
        "description": "Generate random user data"
    },
    {
        "name": "Jokes API",
        "url": "https://official-joke-api.appspot.com/random_joke",
        "description": "Get random jokes"
    },
    {
        "name": "IPify",
        "url": "https://api.ipify.org?format=json",
        "description": "Get your IP address"
    },
    {
        "name": "Agify.io",
        "url": "https://api.agify.io",
        "params": {"name": "Michael"},
        "description": "Predict age from name (has rate limits!)"
    },
    {
        "name": "Genderize.io",
        "url": "https://api.genderize.io",
        "params": {"name": "Alex"},
        "description": "Predict gender from name (has rate limits!)"
    },
    {
        "name": "Nationalize.io",
        "url": "https://api.nationalize.io",
        "params": {"name": "Nathaniel"},
        "description": "Predict nationality from name (has rate limits!)"
    }
]

for i, api in enumerate(working_apis, 1):
    print(f"\n{i}. {api['name']} - {api['description']}")
    print("-" * 70)
    
    try:
        params = api.get("params", {})
        response = limiter.request("GET", api["url"], params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Display relevant data based on API
            if api["name"] == "Dog Images":
                print(f"✓ Image URL: {data.get('message', 'N/A')}")
            elif api["name"] == "Random User":
                user = data.get("results", [{}])[0]
                name = user.get("name", {})
                print(f"✓ User: {name.get('first', '')} {name.get('last', '')}")
                print(f"  Email: {user.get('email', 'N/A')}")
            elif api["name"] == "Jokes API":
                print(f"✓ Setup: {data.get('setup', 'N/A')}")
                print(f"  Punchline: {data.get('punchline', 'N/A')}")
            elif api["name"] == "IPify":
                print(f"✓ IP Address: {data.get('ip', 'N/A')}")
            elif api["name"] == "Agify.io":
                print(f"✓ Name: {data.get('name', 'N/A')}")
                print(f"  Predicted Age: {data.get('age', 'N/A')}")
            elif api["name"] == "Genderize.io":
                print(f"✓ Name: {data.get('name', 'N/A')}")
                print(f"  Gender: {data.get('gender', 'N/A')} ({data.get('probability', 0) * 100:.1f}%)")
            elif api["name"] == "Nationalize.io":
                countries = data.get('country', [])
                if countries:
                    top = countries[0]
                    print(f"✓ Name: {data.get('name', 'N/A')}")
                    print(f"  Top Nationality: {top.get('country_id', 'N/A')} ({top.get('probability', 0) * 100:.1f}%)")
            
            # Check rate limit status
            status = limiter.get_status(api["url"])
            if status:
                print(f"\n📊 Rate Limit Detected:")
                print(f"   Limit: {status.limit}")
                print(f"   Remaining: {status.remaining}")
                print(f"   Utilization: {status.utilization * 100:.1f}%")
                if status.reset_in:
                    print(f"   Resets in: {status.reset_in:.0f} seconds")
            else:
                print("\n📊 No rate limit headers detected (API may not provide them)")
                
        else:
            print(f"✗ Error: Status code {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error: {e}")


# Demonstrate rate limit tracking with multiple requests
print("\n\n" + "=" * 70)
print("Rate Limit Tracking Demo")
print("=" * 70)
print("Making multiple requests to Agify.io to track rate limits...\n")

names = ["Sarah", "John", "Emma", "David", "Lisa"]
for i, name in enumerate(names, 1):
    try:
        url = "https://api.agify.io"
        params = {"name": name}
        response = limiter.request("GET", url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            status = limiter.get_status(url)
            if status:
                print(f"[{i}/{len(names)}] {name}: Age {data.get('age', 'N/A')} | "
                      f"Rate limit: {status.remaining}/{status.limit} remaining")
            else:
                print(f"[{i}/{len(names)}] {name}: Age {data.get('age', 'N/A')}")
    except Exception as e:
        print(f"[{i}/{len(names)}] {name}: Error - {e}")

print("\n" + "=" * 70)
print("✅ Demo Complete!")
print("=" * 70)
print("\nKey Takeaways:")
print("  • smartratelimit automatically detects rate limits from API headers")
print("  • Rate limit status is tracked and updated with each request")
print("  • Works seamlessly across different APIs")
print("  • No manual rate limit management needed!")

