# API Reference

Complete API reference for smartratelimit.

## RateLimiter

Main synchronous rate limiter class.

### `RateLimiter.__init__()`

```python
RateLimiter(
    storage: str = "memory",
    default_limits: Optional[Dict[str, int]] = None,
    headers_map: Optional[Dict[str, str]] = None,
    raise_on_limit: bool = False
)
```

Initialize a rate limiter.

**Parameters:**
- `storage` (str): Storage backend specification
  - `"memory"`: In-memory storage (default)
  - `"sqlite:///path"`: SQLite database path
  - `"redis://host:port"`: Redis connection URL
- `default_limits` (dict, optional): Default rate limits when headers aren't available
  - Keys: `"requests_per_second"`, `"requests_per_minute"`, `"requests_per_hour"`
  - Example: `{"requests_per_minute": 60}`
- `headers_map` (dict, optional): Custom header name mapping
  - Keys: `"limit"`, `"remaining"`, `"reset"`
  - Example: `{"limit": "X-My-Limit"}`
- `raise_on_limit` (bool): If `True`, raise `RateLimitExceeded` instead of waiting

**Returns:** `RateLimiter` instance

### `RateLimiter.request()`

```python
request(method: str, url: str, **kwargs) -> requests.Response
```

Make a rate-limited HTTP request.

**Parameters:**
- `method` (str): HTTP method (GET, POST, PUT, DELETE, PATCH)
- `url` (str): Request URL
- `**kwargs`: Additional arguments passed to `requests.request()`

**Returns:** `requests.Response` object

**Raises:** `RateLimitExceeded` if `raise_on_limit=True` and limit is exceeded

### `RateLimiter.get_status()`

```python
get_status(endpoint: str) -> Optional[RateLimitStatus]
```

Get current rate limit status for an endpoint.

**Parameters:**
- `endpoint` (str): Endpoint URL or domain

**Returns:** `RateLimitStatus` object or `None` if no info available

### `RateLimiter.set_limit()`

```python
set_limit(endpoint: str, limit: int, window: str = "1h") -> None
```

Manually set rate limit for an endpoint.

**Parameters:**
- `endpoint` (str): Endpoint URL or domain
- `limit` (int): Maximum number of requests
- `window` (str): Time window format
  - Formats: `"1h"`, `"30m"`, `"60s"`, `"1d"`

### `RateLimiter.clear()`

```python
clear(endpoint: Optional[str] = None) -> None
```

Clear stored rate limit data.

**Parameters:**
- `endpoint` (str, optional): Specific endpoint to clear, or `None` to clear all

## AsyncRateLimiter

Async rate limiter for use with httpx and aiohttp.

### `AsyncRateLimiter.__init__()`

Same parameters as `RateLimiter.__init__()`.

### `AsyncRateLimiter.arequest_httpx()`

```python
async arequest_httpx(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    **kwargs
) -> httpx.Response
```

Make a rate-limited async HTTP request using httpx.

**Parameters:**
- `client`: `httpx.AsyncClient` instance
- `method` (str): HTTP method
- `url` (str): Request URL
- `**kwargs`: Additional arguments for `client.request()`

**Returns:** `httpx.Response` object

### `AsyncRateLimiter.arequest_aiohttp()`

```python
async arequest_aiohttp(
    session: aiohttp.ClientSession,
    method: str,
    url: str,
    **kwargs
) -> aiohttp.ClientResponse
```

Make a rate-limited async HTTP request using aiohttp.

**Parameters:**
- `session`: `aiohttp.ClientSession` instance
- `method` (str): HTTP method
- `url` (str): Request URL
- `**kwargs`: Additional arguments for `session.request()`

**Returns:** `aiohttp.ClientResponse` object

## RetryHandler

Handler for retrying requests with configurable strategies.

### `RetryHandler.__init__()`

```python
RetryHandler(config: Optional[RetryConfig] = None)
```

Initialize retry handler.

**Parameters:**
- `config` (RetryConfig, optional): Retry configuration (uses defaults if None)

### `RetryHandler.retry_sync()`

```python
retry_sync(func: Callable[[], T], *args, **kwargs) -> T
```

Retry a synchronous function.

**Parameters:**
- `func`: Function to retry
- `*args`, `**kwargs`: Arguments for function

**Returns:** Result of function call

**Raises:** Last exception if all retries fail

### `RetryHandler.retry_async()`

```python
async retry_async(func: Callable, *args, **kwargs) -> T
```

Retry an async function.

**Parameters:**
- `func`: Async function to retry
- `*args`, `**kwargs`: Arguments for function

**Returns:** Result of async function call

## RetryConfig

Configuration for retry behavior.

### `RetryConfig.__init__()`

```python
RetryConfig(
    max_retries: int = 3,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    retry_on_status: Optional[list] = None
)
```

**Parameters:**
- `max_retries` (int): Maximum number of retry attempts
- `strategy` (RetryStrategy): Retry strategy enum
- `base_delay` (float): Base delay in seconds
- `max_delay` (float): Maximum delay in seconds
- `backoff_factor` (float): Factor for exponential backoff
- `retry_on_status` (list, optional): HTTP status codes to retry on (default: [429, 503, 504])

## RetryStrategy

Enum for retry strategies:
- `RetryStrategy.EXPONENTIAL`: Exponential backoff
- `RetryStrategy.LINEAR`: Linear backoff
- `RetryStrategy.FIXED`: Fixed delay
- `RetryStrategy.NONE`: No retry

## MetricsCollector

Collects and exports rate limit metrics.

### `MetricsCollector.__init__()`

Initialize metrics collector.

### `MetricsCollector.record_request()`

```python
record_request(
    endpoint: str,
    status_code: int,
    rate_limit_status: Optional[RateLimitStatus] = None
) -> None
```

Record a request and its rate limit status.

### `MetricsCollector.get_metrics()`

```python
get_metrics(endpoint: Optional[str] = None) -> Dict
```

Get metrics for endpoint(s).

**Parameters:**
- `endpoint` (str, optional): Specific endpoint, or None for all

**Returns:** Metrics dictionary

### `MetricsCollector.export_prometheus()`

```python
export_prometheus() -> str
```

Export metrics in Prometheus format.

**Returns:** Prometheus metrics string

### `MetricsCollector.export_json()`

```python
export_json() -> str
```

Export metrics as JSON.

**Returns:** JSON string

## RateLimitStatus

Status information about current rate limits.

### Properties

- `endpoint` (str): Endpoint URL
- `limit` (int): Total rate limit
- `remaining` (int): Remaining requests
- `reset_time` (datetime, optional): When the limit resets
- `window` (timedelta, optional): Time window for the limit
- `reset_in` (float, optional): Seconds until reset (property)
- `is_exceeded` (bool): Whether limit is exceeded (property)
- `utilization` (float): Utilization percentage 0.0-1.0 (property)

## Exceptions

### `RateLimitExceeded`

Exception raised when rate limit is exceeded and `raise_on_limit=True`.

```python
class RateLimitExceeded(Exception):
    pass
```

