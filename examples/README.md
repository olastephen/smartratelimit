# Examples

Runnable example scripts demonstrating smartratelimit features.

## Quick Start Examples

- **`free_apis_simple.py`** - Simple examples using free APIs (no key required)
- **`free_apis_demo.py`** - Comprehensive demo with 10+ free APIs
- **`free_apis_working.py`** - Focused demo showing rate limit detection
- **`free_apis_batch.py`** - Batch processing examples

## Real API Examples

- **`rapidapi_email_validation.py`** - Simple RapidAPI email validation
- **`rapidapi_batch_validation.py`** - Batch validation with RapidAPI
- **`openweather_simple.py`** - Simple OpenWeatherMap example
- **`openweather_complete.py`** - Complete OpenWeatherMap demo
- **`integrate_rapidapi.py`** - Complete integration guide

## Feature-Specific Examples

- **`v0_2_features.py`** - SQLite and Redis storage examples
- **`v0_3_async.py`** - Async/await with httpx and aiohttp
- **`v0_3_retry.py`** - Retry strategies examples
- **`v0_3_metrics.py`** - Metrics collection examples

## Running Examples

### Basic Examples (No API Key Required)

```bash
# Free APIs examples
python3 examples/free_apis_simple.py
python3 examples/free_apis_demo.py
python3 examples/free_apis_working.py
```

### API Examples (Require API Keys)

```bash
# OpenWeatherMap (replace YOUR_API_KEY)
# Edit the file first to add your API key
python3 examples/openweather_simple.py

# RapidAPI (replace YOUR_API_KEY)
# Edit the file first to add your API key
python3 examples/rapidapi_email_validation.py
```

### Feature Examples

```bash
# Storage backends
python3 examples/v0_2_features.py

# Async features (requires httpx or aiohttp)
pip install httpx  # or aiohttp
python3 examples/v0_3_async.py

# Retry strategies
python3 examples/v0_3_retry.py

# Metrics collection
python3 examples/v0_3_metrics.py
```

## Note on API Keys

Examples that use APIs requiring keys (RapidAPI, OpenWeatherMap) use placeholder keys:
- `YOUR_API_KEY` - Replace with your actual API key
- Get RapidAPI key: https://rapidapi.com
- Get OpenWeatherMap key: https://openweathermap.org/api

## More Documentation

- 📖 [Quick Start Guide](../docs/QUICK_START.md)
- 📚 [Complete Tutorial](../docs/TUTORIAL.md)
- 💻 [Examples Documentation](../docs/EXAMPLES.md)
- 📋 [API Reference](../docs/API_REFERENCE.md)

