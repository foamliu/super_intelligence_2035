# Fix for UnicodeError when requesting URLs with leading dot in domain

## Issue Description
When requesting a URL like `http://.example.com`, requests raises a `UnicodeError` instead of the expected `InvalidURL` exception.

## Root Cause
In the `prepare_url` method in `requests/models.py`, the hostname IDNA encoding step is not wrapped in a try-except block to catch UnicodeError exceptions that occur when the domain has invalid labels (like empty leading labels).

## Fix
Modify the IDNA encoding step in `prepare_url` to catch UnicodeError and convert it to InvalidURL:

### Before:
```python
host = host.encode('idna').decode('ascii')
```

### After:
```python
try:
    host = host.encode('idna').decode('ascii')
except UnicodeError:
    raise InvalidURL("URL has an invalid label.")
```

## Test Case
```python
import requests

try:
    requests.get("http://.example.com")
except requests.exceptions.InvalidURL as e:
    assert "URL has an invalid label." in str(e)
    print("✓ Correctly raised InvalidURL as expected")
except Exception as e:
    print(f"✗ Wrong exception raised: {type(e).__name__}: {e}")
    raise
```

## Expected Result
Running the test should output:
```
✓ Correctly raised InvalidURL as expected
```

## Actual Result Before Fix
Running the test would output:
```
✗ Wrong exception raised: UnicodeError: encoding with 'idna' codec failed (UnicodeError: label empty or too long)
```
