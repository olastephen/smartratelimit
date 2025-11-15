"""
Batch Testing: Multiple requests to free APIs with smartratelimit.

This demonstrates how smartratelimit handles multiple sequential requests
across different APIs automatically.
"""

from smartratelimit import RateLimiter
import time

# Create rate limiter
limiter = RateLimiter()

# List of free APIs to test
apis = [
    {
        "name": "Cat Facts",
        "url": "https://cat-fact.herokuapp.com/facts",
        "method": "GET"
    },
    {
        "name": "Bitcoin Price",
        "url": "https://api.coindesk.com/v1/bpi/currentprice.json",
        "method": "GET"
    },
    {
        "name": "Random Activity",
        "url": "https://www.boredapi.com/api/activity",
        "method": "GET"
    },
    {
        "name": "Dog Image",
        "url": "https://dog.ceo/api/breeds/image/random",
        "method": "GET"
    },
    {
        "name": "Random User",
        "url": "https://randomuser.me/api/",
        "method": "GET"
    },
    {
        "name": "Random Joke",
        "url": "https://official-joke-api.appspot.com/random_joke",
        "method": "GET"
    },
    {
        "name": "IP Address",
        "url": "https://api.ipify.org?format=json",
        "method": "GET"
    },
    {
        "name": "Age Prediction",
        "url": "https://api.agify.io",
        "method": "GET",
        "params": {"name": "Sarah"}
    },
    {
        "name": "Gender Prediction",
        "url": "https://api.genderize.io",
        "method": "GET",
        "params": {"name": "Jordan"}
    },
    {
        "name": "Nationality Prediction",
        "url": "https://api.nationalize.io",
        "method": "GET",
        "params": {"name": "David"}
    }
]

print("=" * 70)
print("Batch Testing Free APIs with smartratelimit")
print("=" * 70)
print(f"Testing {len(apis)} APIs sequentially...\n")

results = []
start_time = time.time()

for i, api in enumerate(apis, 1):
    try:
        print(f"[{i}/{len(apis)}] {api['name']}...", end=" ")
        
        # Make request
        params = api.get("params", {})
        response = limiter.request(api["method"], api["url"], params=params)
        
        if response.status_code == 200:
            print("✓ Success")
            results.append({
                "name": api["name"],
                "status": "success",
                "status_code": response.status_code
            })
        else:
            print(f"✗ Failed ({response.status_code})")
            results.append({
                "name": api["name"],
                "status": "failed",
                "status_code": response.status_code
            })
        
        # Check rate limit status
        status = limiter.get_status(api["url"])
        if status:
            print(f"     Rate limit: {status.remaining}/{status.limit} remaining")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        results.append({
            "name": api["name"],
            "status": "error",
            "error": str(e)
        })

elapsed = time.time() - start_time

# Summary
print("\n" + "=" * 70)
print("Results Summary")
print("=" * 70)
successful = sum(1 for r in results if r["status"] == "success")
failed = len(results) - successful

print(f"Total APIs tested: {len(apis)}")
print(f"Successful: {successful}")
print(f"Failed: {failed}")
print(f"Time elapsed: {elapsed:.2f} seconds")
print(f"Average time per request: {elapsed/len(apis):.2f} seconds")

if failed > 0:
    print("\nFailed APIs:")
    for r in results:
        if r["status"] != "success":
            print(f"  - {r['name']}: {r.get('error', r.get('status_code', 'Unknown'))}")

print("=" * 70)

