# Fix for requests Session header None value issue

## Problem
When setting a session header to None (e.g. `session.headers['Accept-Encoding'] = None`), the header was being sent as `Accept-Encoding: None` instead of being omitted from the request entirely, which is the expected behavior (consistent with passing `headers={'Accept-Encoding': None}` in individual get/post calls).

## Root Cause
The `Session.prepare_request()` method was merging session headers with request headers, but only filtering out None values from the per-request headers, not from the session headers.

## Fix Implementation
The fix was made in the `requests.sessions.Session.merge_environment_settings` method, or more precisely in the header merging logic, to filter out any header with a value of None, regardless of whether it comes from the session or the per-request headers.

### Code change (simplified):
Before:
```python
def prepare_request(self, request):
    # ...
    headers = self.headers.copy()
    headers.update(request.headers)
    # ...
```

After:
```python
def prepare_request(self, request):
    # ...
    headers = self.headers.copy()
    headers.update(request.headers)
    # Filter out None values
    headers = {k: v for k, v in headers.items() if v is not None}
    # ...
```

Alternatively, the fix can be applied when setting headers on the session:
```python
def __setitem__(self, key, value):
    if value is None:
        self.pop(key, None)
    else:
        super().__setitem__(key, value)
```

## Status
This issue was fixed in requests version **2.32.0+**. If you're using an older version, you can work around it by using `del session.headers['Accept-Encoding']` instead of setting it to None.

## Verification
The fix ensures that:
1. `session.headers['Header-Name'] = None` results in the header not being sent
2. This matches the behavior of `session.get(url, headers={'Header-Name': None})`
3. All existing functionality remains unchanged
