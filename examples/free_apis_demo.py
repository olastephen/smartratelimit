"""
Demo: Testing smartratelimit with free APIs from apipheny.io/free-api/

This demonstrates how smartratelimit automatically handles rate limits
across multiple different free APIs.
"""

from smartratelimit import RateLimiter
import json

# Create rate limiter
limiter = RateLimiter()

print("=" * 70)
print("Testing smartratelimit with Free APIs")
print("=" * 70)


# 1. Cat Facts API
print("\n1️⃣  Cat Facts API")
print("-" * 70)
try:
    url = "https://cat-fact.herokuapp.com/facts"
    response = limiter.request("GET", url)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Got {len(data)} cat facts")
        if data:
            print(f"  Sample: {data[0].get('text', 'N/A')[:80]}...")
    status = limiter.get_status(url)
    if status:
        print(f"  Rate limit: {status.remaining}/{status.limit} remaining")
except Exception as e:
    print(f"✗ Error: {e}")


# 2. CoinDesk Bitcoin Price
print("\n2️⃣  CoinDesk Bitcoin Price")
print("-" * 70)
try:
    url = "https://api.coindesk.com/v1/bpi/currentprice.json"
    response = limiter.request("GET", url)
    if response.status_code == 200:
        data = response.json()
        bpi = data.get("bpi", {}).get("USD", {})
        print(f"✓ Bitcoin Price: ${bpi.get('rate', 'N/A')}")
        print(f"  Updated: {data.get('time', {}).get('updated', 'N/A')}")
    status = limiter.get_status(url)
    if status:
        print(f"  Rate limit: {status.remaining}/{status.limit} remaining")
except Exception as e:
    print(f"✗ Error: {e}")


# 3. Bored API - Random Activity
print("\n3️⃣  Bored API - Random Activity")
print("-" * 70)
try:
    url = "https://www.boredapi.com/api/activity"
    response = limiter.request("GET", url)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Activity: {data.get('activity', 'N/A')}")
        print(f"  Type: {data.get('type', 'N/A')}")
        print(f"  Participants: {data.get('participants', 'N/A')}")
    status = limiter.get_status(url)
    if status:
        print(f"  Rate limit: {status.remaining}/{status.limit} remaining")
except Exception as e:
    print(f"✗ Error: {e}")


# 4. Dog Images API
print("\n4️⃣  Dog Images API")
print("-" * 70)
try:
    url = "https://dog.ceo/api/breeds/image/random"
    response = limiter.request("GET", url)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Random dog image: {data.get('message', 'N/A')}")
        print(f"  Status: {data.get('status', 'N/A')}")
    status = limiter.get_status(url)
    if status:
        print(f"  Rate limit: {status.remaining}/{status.limit} remaining")
except Exception as e:
    print(f"✗ Error: {e}")


# 5. Random User API
print("\n5️⃣  Random User API")
print("-" * 70)
try:
    url = "https://randomuser.me/api/"
    response = limiter.request("GET", url)
    if response.status_code == 200:
        data = response.json()
        if data.get("results"):
            user = data["results"][0]
            name = user.get("name", {})
            print(f"✓ Random User: {name.get('first', '')} {name.get('last', '')}")
            print(f"  Email: {user.get('email', 'N/A')}")
            print(f"  Location: {user.get('location', {}).get('city', 'N/A')}")
    status = limiter.get_status(url)
    if status:
        print(f"  Rate limit: {status.remaining}/{status.limit} remaining")
except Exception as e:
    print(f"✗ Error: {e}")


# 6. Jokes API
print("\n6️⃣  Jokes API")
print("-" * 70)
try:
    url = "https://official-joke-api.appspot.com/random_joke"
    response = limiter.request("GET", url)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Joke ({data.get('type', 'N/A')}):")
        print(f"  Setup: {data.get('setup', 'N/A')}")
        print(f"  Punchline: {data.get('punchline', 'N/A')}")
    status = limiter.get_status(url)
    if status:
        print(f"  Rate limit: {status.remaining}/{status.limit} remaining")
except Exception as e:
    print(f"✗ Error: {e}")


# 7. IPify - Get IP Address
print("\n7️⃣  IPify - Get IP Address")
print("-" * 70)
try:
    url = "https://api.ipify.org?format=json"
    response = limiter.request("GET", url)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Your IP Address: {data.get('ip', 'N/A')}")
    status = limiter.get_status(url)
    if status:
        print(f"  Rate limit: {status.remaining}/{status.limit} remaining")
except Exception as e:
    print(f"✗ Error: {e}")


# 8. Agify.io - Predict Age
print("\n8️⃣  Agify.io - Predict Age from Name")
print("-" * 70)
try:
    url = "https://api.agify.io"
    params = {"name": "Michael"}
    response = limiter.request("GET", url, params=params)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Name: {data.get('name', 'N/A')}")
        print(f"  Predicted Age: {data.get('age', 'N/A')}")
        print(f"  Count: {data.get('count', 'N/A')} occurrences")
    status = limiter.get_status(url)
    if status:
        print(f"  Rate limit: {status.remaining}/{status.limit} remaining")
except Exception as e:
    print(f"✗ Error: {e}")


# 9. Genderize.io - Predict Gender
print("\n9️⃣  Genderize.io - Predict Gender from Name")
print("-" * 70)
try:
    url = "https://api.genderize.io"
    params = {"name": "Alex"}
    response = limiter.request("GET", url, params=params)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Name: {data.get('name', 'N/A')}")
        print(f"  Predicted Gender: {data.get('gender', 'N/A')}")
        print(f"  Probability: {data.get('probability', 0) * 100:.1f}%")
    status = limiter.get_status(url)
    if status:
        print(f"  Rate limit: {status.remaining}/{status.limit} remaining")
except Exception as e:
    print(f"✗ Error: {e}")


# 10. Nationalize.io - Predict Nationality
print("\n🔟  Nationalize.io - Predict Nationality from Name")
print("-" * 70)
try:
    url = "https://api.nationalize.io"
    params = {"name": "Nathaniel"}
    response = limiter.request("GET", url, params=params)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Name: {data.get('name', 'N/A')}")
        countries = data.get('country', [])
        if countries:
            top = countries[0]
            print(f"  Top Nationality: {top.get('country_id', 'N/A')} ({top.get('probability', 0) * 100:.1f}%)")
    status = limiter.get_status(url)
    if status:
        print(f"  Rate limit: {status.remaining}/{status.limit} remaining")
except Exception as e:
    print(f"✗ Error: {e}")


# Summary
print("\n" + "=" * 70)
print("Summary")
print("=" * 70)
print("✓ Tested 10 different free APIs")
print("✓ All requests handled automatically by smartratelimit")
print("✓ Rate limits detected and tracked where available")
print("=" * 70)

