# Fix for requests bytes method issue (Python 3)

## Problem
When using Python 3 with requests 2.4.3 and python-neutronclient 2.3.9, HTTP methods passed as bytes (like `b'GET'`) get converted to the literal string `"b'GET'"` instead of being decoded to `"GET"`. This causes 404 Not Found errors.

## Root Cause
In requests 2.4.3, the `PreparedRequest.prepare_method` function uses:
```python
method = builtin_str(method)
```
On Python 3, `str(b'GET')` returns `"b'GET'"` (the repr of the bytes object), not the decoded string `"GET"`.

## Solution
### Option 1: Patch the requests source code (permanent fix)
1. Locate your requests installation:
   ```bash
   python -c "import requests; print(requests.__file__)"
   ```
2. Open `requests/models.py` in an editor
3. Find the `prepare_method` function (around line ~300 in 2.4.3):
   ```python
   def prepare_method(self, method):
       """Prepares the given HTTP method."""
       if method is not None:
           method = builtin_str(method)
       self.method = method.upper() if method is not None else method
   ```
4. Modify it to handle bytes correctly:
   ```python
   def prepare_method(self, method):
       """Prepares the given HTTP method."""
       if method is not None:
           if isinstance(method, bytes):
               method = method.decode('utf-8')
           method = builtin_str(method)
       self.method = method.upper() if method is not None else method
   ```

### Option 2: Runtime patch (no source code changes needed)
Add this code to your application before making any requests:
```python
import requests
from requests.models import PreparedRequest

original_prepare_method = PreparedRequest.prepare_method

def patched_prepare_method(self, method):
    if method is not None and isinstance(method, bytes):
        method = method.decode('utf-8')
    return original_prepare_method(self, method)

PreparedRequest.prepare_method = patched_prepare_method
```

### Option 3: Upgrade requests (recommended if possible)
This bug was fixed in requests versions >= 2.5.0. Upgrade to a newer version:
```bash
pip install --upgrade requests
```

## Verification
After applying the fix, test it:
```python
import requests
req = requests.Request(b'GET', 'https://httpbin.org/get')
prep = req.prepare()
assert prep.method == "GET", f"Expected 'GET', got {repr(prep.method)}"
print("Fix works correctly!")
```
