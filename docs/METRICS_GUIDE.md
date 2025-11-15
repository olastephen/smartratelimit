# Metrics Guide

Complete guide to collecting and exporting rate limit metrics.

## Table of Contents

1. [MetricsCollector Overview](#metricscollector-overview)
2. [Collecting Metrics](#collecting-metrics)
3. [Export Formats](#export-formats)
4. [Prometheus Export](#prometheus-export)
5. [JSON Export](#json-export)
6. [Examples](#examples)

## MetricsCollector Overview

`MetricsCollector` tracks rate limit usage and provides export functionality.

### Import

```python
from smartratelimit import MetricsCollector
```

## Collecting Metrics

### Basic Usage

```python
from smartratelimit import MetricsCollector, RateLimiter

# Create metrics collector
metrics = MetricsCollector()

# Create rate limiter
limiter = RateLimiter()

# Make requests and record metrics
response = limiter.request("GET", "https://api.example.com/data")

# Record the request
metrics.record_request(
    endpoint="https://api.example.com",
    status_code=response.status_code,
    rate_limit_remaining=100  # From response headers or limiter.get_status()
)
```

### Example: Tracking Multiple Requests

```python
from smartratelimit import MetricsCollector, RateLimiter

metrics = MetricsCollector()
limiter = RateLimiter()

url = "https://api.agify.io"
names = ["Michael", "Sarah", "Alex", "Emma"]

for name in names:
    response = limiter.request("GET", url, params={"name": name})
    
    # Get rate limit status
    status = limiter.get_status(url)
    remaining = status.remaining if status else None
    
    # Record metrics
    metrics.record_request(
        endpoint=url,
        status_code=response.status_code,
        rate_limit_remaining=remaining
    )

# Export metrics
print(metrics.export_json())
```

### Example: Tracking with Free APIs

```python
from smartratelimit import MetricsCollector, RateLimiter

metrics = MetricsCollector()
limiter = RateLimiter()

# Track requests to multiple APIs
apis = [
    "https://randomuser.me/api/",
    "https://dog.ceo/api/breeds/image/random",
    "https://official-joke-api.appspot.com/random_joke"
]

for api_url in apis:
    response = limiter.request("GET", api_url)
    
    status = limiter.get_status(api_url)
    remaining = status.remaining if status else None
    
    metrics.record_request(
        endpoint=api_url,
        status_code=response.status_code,
        rate_limit_remaining=remaining
    )

# View collected metrics
print(f"Total requests: {len(metrics.requests)}")
```

## Export Formats

### Prometheus Export

Prometheus format for monitoring systems.

```python
from smartratelimit import MetricsCollector

metrics = MetricsCollector()

# Record some requests
metrics.record_request("https://api.example.com", 200, 100)
metrics.record_request("https://api.example.com", 200, 99)
metrics.record_request("https://api.example.com", 429, 0)

# Export in Prometheus format
prometheus_metrics = metrics.export_prometheus()
print(prometheus_metrics)
```

### JSON Export

JSON format for custom dashboards or logging.

```python
from smartratelimit import MetricsCollector
import json

metrics = MetricsCollector()

# Record requests
metrics.record_request("https://api.example.com", 200, 100)
metrics.record_request("https://api.example.com", 200, 99)

# Export as JSON
json_metrics = metrics.export_json()
print(json.dumps(json_metrics, indent=2))
```

## Prometheus Export

### Example: Complete Prometheus Setup

```python
from smartratelimit import MetricsCollector, RateLimiter
from http.server import HTTPServer, BaseHTTPRequestHandler

metrics = MetricsCollector()
limiter = RateLimiter()

class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(metrics.export_prometheus().encode())
        else:
            self.send_response(404)
            self.end_headers()

# Make some requests
url = "https://api.agify.io"
for name in ["Michael", "Sarah", "Alex"]:
    response = limiter.request("GET", url, params={"name": name})
    status = limiter.get_status(url)
    metrics.record_request(url, response.status_code, status.remaining if status else None)

# Start metrics server
server = HTTPServer(('localhost', 8000), MetricsHandler)
print("Metrics server running on http://localhost:8000/metrics")
# server.serve_forever()
```

### Example: Prometheus Metrics Format

```python
from smartratelimit import MetricsCollector

metrics = MetricsCollector()

# Record requests
metrics.record_request("https://api.example.com/data", 200, 100)
metrics.record_request("https://api.example.com/data", 200, 99)
metrics.record_request("https://api.example.com/data", 429, 0)

# Export
prometheus_output = metrics.export_prometheus()
print(prometheus_output)

# Output format:
# # HELP ratelimit_requests_total Total number of requests
# # TYPE ratelimit_requests_total counter
# ratelimit_requests_total{endpoint="https://api.example.com/data"} 3
# # HELP ratelimit_remaining Current remaining rate limit
# # TYPE ratelimit_remaining gauge
# ratelimit_remaining{endpoint="https://api.example.com/data"} 0
```

## JSON Export

### Example: JSON Metrics

```python
from smartratelimit import MetricsCollector
import json

metrics = MetricsCollector()

# Record requests
metrics.record_request("https://api.example.com/data", 200, 100)
metrics.record_request("https://api.example.com/data", 200, 99)
metrics.record_request("https://api.example.com/data", 429, 0)

# Export as JSON
json_output = metrics.export_json()
print(json.dumps(json_output, indent=2))

# Output:
# {
#   "total_requests": 3,
#   "endpoints": {
#     "https://api.example.com/data": {
#       "requests": 3,
#       "successful": 2,
#       "failed": 1,
#       "average_remaining": 66.33
#     }
#   }
# }
```

### Example: Save Metrics to File

```python
from smartratelimit import MetricsCollector, RateLimiter
import json
from datetime import datetime

metrics = MetricsCollector()
limiter = RateLimiter()

# Make requests and collect metrics
url = "https://api.agify.io"
names = ["Michael", "Sarah", "Alex", "Emma", "David"]

for name in names:
    response = limiter.request("GET", url, params={"name": name})
    status = limiter.get_status(url)
    metrics.record_request(
        url,
        response.status_code,
        status.remaining if status else None
    )

# Export and save
metrics_data = metrics.export_json()
metrics_data["timestamp"] = datetime.now().isoformat()

with open("metrics.json", "w") as f:
    json.dump(metrics_data, f, indent=2)

print("Metrics saved to metrics.json")
```

## Examples

### Example: Real-Time Metrics Dashboard

```python
from smartratelimit import MetricsCollector, RateLimiter
import time

metrics = MetricsCollector()
limiter = RateLimiter()

def make_request_and_track(url):
    response = limiter.request("GET", url)
    status = limiter.get_status(url)
    metrics.record_request(
        url,
        response.status_code,
        status.remaining if status else None
    )
    return response

# Make requests
url = "https://api.agify.io"
for name in ["Michael", "Sarah", "Alex"]:
    make_request_and_track(url)
    time.sleep(1)

# Display metrics
json_metrics = metrics.export_json()
print(f"Total Requests: {json_metrics['total_requests']}")
for endpoint, data in json_metrics['endpoints'].items():
    print(f"\n{endpoint}:")
    print(f"  Requests: {data['requests']}")
    print(f"  Successful: {data['successful']}")
    print(f"  Failed: {data['failed']}")
    print(f"  Avg Remaining: {data['average_remaining']:.2f}")
```

### Example: Metrics with Multiple APIs

```python
from smartratelimit import MetricsCollector, RateLimiter

metrics = MetricsCollector()
limiter = RateLimiter()

# Track multiple APIs
apis = {
    "Random User": "https://randomuser.me/api/",
    "Dog Images": "https://dog.ceo/api/breeds/image/random",
    "Jokes": "https://official-joke-api.appspot.com/random_joke",
    "Agify": "https://api.agify.io"
}

# Make requests to each API
for name, url in apis.items():
    if "agify" in url.lower():
        response = limiter.request("GET", url, params={"name": "Michael"})
    else:
        response = limiter.request("GET", url)
    
    status = limiter.get_status(url)
    metrics.record_request(
        url,
        response.status_code,
        status.remaining if status else None
    )

# Export metrics
json_metrics = metrics.export_json()
print(json.dumps(json_metrics, indent=2))
```

### Example: Periodic Metrics Export

```python
from smartratelimit import MetricsCollector, RateLimiter
import json
import time
from datetime import datetime

metrics = MetricsCollector()
limiter = RateLimiter()

def export_metrics_periodically(interval=60):
    """Export metrics every N seconds."""
    url = "https://api.agify.io"
    request_count = 0
    
    while True:
        # Make a request
        response = limiter.request("GET", url, params={"name": "Test"})
        status = limiter.get_status(url)
        metrics.record_request(url, response.status_code, status.remaining if status else None)
        request_count += 1
        
        # Export every N requests
        if request_count % 10 == 0:
            metrics_data = metrics.export_json()
            metrics_data["export_time"] = datetime.now().isoformat()
            
            filename = f"metrics_{int(time.time())}.json"
            with open(filename, "w") as f:
                json.dump(metrics_data, f, indent=2)
            
            print(f"Metrics exported to {filename}")
        
        time.sleep(interval)

# Run (in production, use a scheduler)
# export_metrics_periodically(60)
```

## More Resources

- 📖 [Quick Start Guide](QUICK_START.md)
- 📚 [Complete Tutorial](TUTORIAL.md)
- 💻 [Examples](EXAMPLES.md)
- 📊 [API Reference](API_REFERENCE.md)

