# REST API Integration Documentation

## Overview

This project now includes REST API integration to send solar inverter data to external services, specifically ChargeHQ. The data is automatically sent alongside the existing MQTT functionality.

## Features

- **Rate Limiting**: Data is sent to REST endpoints no more than once every 60 seconds to respect API limits
- **Error Handling**: Comprehensive error handling with logging for connection issues, timeouts, and API errors
- **Non-blocking**: REST calls don't interfere with the main MQTT functionality
- **Configurable**: Can be easily enabled/disabled via configuration

## Configuration

Add the following to your `config.py` file:

```python
# [ MQTT ]
# Enable/disable MQTT functionality
MQTT_ENABLED = True

# ChargeHQ API key
CHARGEHQ_APIKEY = "your-api-key-here"

# [ REST CLIENT ]
# Enable sending data to REST endpoints (ChargeHQ)
REST_ENABLED = False  # Default: disabled
# Default consumption value to use when actual consumption data is not available
REST_DEFAULT_CONSUMPTION_KW = 1.0
# Maximum frequency for REST API calls (in seconds)
REST_MAX_FREQUENCY_SECONDS = 60  # Default: 60 seconds
```

### Configuration Options

- **`MQTT_ENABLED`**: Boolean switch to enable/disable all MQTT functionality (default: `True`)
- **`REST_ENABLED`**: Boolean switch to enable/disable REST API calls (default: `False`)
- **`REST_MAX_FREQUENCY_SECONDS`**: Maximum frequency for REST API calls in seconds (default: `60`)
- **`REST_DEFAULT_CONSUMPTION_KW`**: Default consumption value when actual consumption data is not available (default: `1.0`)

### Flexible Operation Modes

The system now supports different operation modes:

1. **MQTT Only** (`MQTT_ENABLED=True`, `REST_ENABLED=False`): Traditional MQTT-only operation
2. **REST Only** (`MQTT_ENABLED=False`, `REST_ENABLED=True`): Send data only to REST endpoints
3. **Both** (`MQTT_ENABLED=True`, `REST_ENABLED=True`): Send data to both MQTT and REST endpoints
4. **Neither** (`MQTT_ENABLED=False`, `REST_ENABLED=False`): Data logging only (useful for debugging)

## Data Format

The system sends data to ChargeHQ in the following JSON format:

```json
{
  "apiKey": "your-api-key",
  "siteMeters": {
    "consumption_kw": 1.0,
    "net_import_kw": -1.5,
    "production_kw": 2.5
  }
}
```

Where:
- `production_kw`: Solar production from inverter (p_ac1 converted from watts to kW)
- `consumption_kw`: Energy consumption (configurable default, currently 1.0kW)
- `net_import_kw`: Calculated as consumption_kw - production_kw (negative means exporting)

## API Endpoint

- **URL**: `https://api.chargehq.net/api/public/push-solar-data`
- **Method**: POST
- **Content-Type**: application/json
- **Timeout**: 10 seconds

## Rate Limiting

The system implements configurable rate limiting:
- Frequency controlled by `REST_MAX_FREQUENCY_SECONDS` configuration (default: 60 seconds)
- Thread-safe implementation using locks
- Automatic skip of calls that would exceed rate limits
- Logging of rate-limited attempts

You can adjust the frequency by changing the configuration:
```python
REST_MAX_FREQUENCY_SECONDS = 120  # Send data every 2 minutes instead of 1 minute
```

## Error Handling

The system handles various error scenarios:
- Network connectivity issues
- API timeouts
- HTTP error responses
- Missing configuration
- Invalid API keys

All errors are logged but don't affect the main MQTT functionality.

## Testing

Use the included test script to verify REST functionality:

```bash
python test_rest.py
```

This will:
1. Send test data to the ChargeHQ API
2. Verify rate limiting works correctly
3. Show detailed logging output

## Files Modified/Added

- `rest_client.py`: New module containing the ChargeHQ REST client
- `trannergy_parser.py`: Modified to include REST functionality
- `config.py`: Added REST configuration options
- `requirements.txt`: Added `requests` dependency
- `test_rest.py`: Test script for REST functionality

## Dependencies

The REST functionality requires the `requests` library:

```bash
pip install -r requirements.txt
```

## Integration

The REST functionality is automatically integrated into the existing data flow:
1. Inverter data is received and parsed (existing functionality)
2. Data is published to MQTT (existing functionality)
3. Data is sent to REST endpoint (new functionality)

The REST integration is non-blocking and won't affect MQTT performance or reliability.

## TODO

- add support for a consumption REST endpoint
- package up as installable module / service that can run on startup in windows
- improve test coverage