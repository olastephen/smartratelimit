"""Examples demonstrating v0.3.0 metrics features."""

from smartratelimit import RateLimiter
from smartratelimit.metrics import MetricsCollector


def example_metrics_collection():
    """Example: Collecting and viewing metrics."""
    print("=== Metrics Collection ===")
    
    limiter = RateLimiter()
    metrics = MetricsCollector()
    
    # Make some requests
    urls = [
        'https://api.github.com/users/octocat',
        'https://api.github.com/users/torvalds',
    ]
    
    for url in urls:
        try:
            response = limiter.request('GET', url)
            status = limiter.get_status(url)
            metrics.record_request(url, response.status_code, status)
            print(f"Request to {url}: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
    
    # View metrics
    print("\nMetrics:")
    all_metrics = metrics.get_metrics()
    for endpoint, endpoint_metrics in all_metrics.items():
        print(f"\n{endpoint}:")
        print(f"  Total requests: {endpoint_metrics['total_requests']}")
        print(f"  Successful: {endpoint_metrics['successful_requests']}")
        print(f"  Rate limited: {endpoint_metrics['rate_limited_requests']}")
        print(f"  Other errors: {endpoint_metrics['other_errors']}")
    print()


def example_prometheus_export():
    """Example: Exporting metrics in Prometheus format."""
    print("=== Prometheus Export ===")
    
    limiter = RateLimiter()
    metrics = MetricsCollector()
    
    # Make a request
    try:
        response = limiter.request('GET', 'https://api.github.com/users/octocat')
        status = limiter.get_status('https://api.github.com')
        metrics.record_request('https://api.github.com', response.status_code, status)
    except Exception as e:
        print(f"Error: {e}")
    
    # Export in Prometheus format
    prometheus_metrics = metrics.export_prometheus()
    print(prometheus_metrics)
    print()


def example_json_export():
    """Example: Exporting metrics as JSON."""
    print("=== JSON Export ===")
    
    limiter = RateLimiter()
    metrics = MetricsCollector()
    
    # Make a request
    try:
        response = limiter.request('GET', 'https://api.github.com/users/octocat')
        status = limiter.get_status('https://api.github.com')
        metrics.record_request('https://api.github.com', response.status_code, status)
    except Exception as e:
        print(f"Error: {e}")
    
    # Export as JSON
    json_metrics = metrics.export_json()
    print(json_metrics)
    print()


if __name__ == "__main__":
    example_metrics_collection()
    example_prometheus_export()
    example_json_export()

