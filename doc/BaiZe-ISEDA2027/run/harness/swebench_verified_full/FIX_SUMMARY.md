# Fix Summary: _pytest.capture.EncodedFile mode should not include `b` (binary)

## Issue
When youtube-dl logs to pytest captured output, it raises a TypeError:
```
TypeError: write() argument must be str, not bytes
```
This happens because youtube-dl checks for `b` in `out.mode` to decide whether to write bytes or strings. `EncodedFile` incorrectly inherited the binary mode from its underlying buffer, even though its `write()` method only accepts strings.

## Root Cause
The `EncodedFile` class uses `__getattr__` to forward all unknown attributes to the underlying binary buffer, so accessing `.mode` returned the buffer's binary mode (including 'b'). But the `write()` method expects string inputs and encodes them internally.

## Fix
Added a `mode` property to `EncodedFile` that removes the 'b' character from the underlying buffer's mode:
```python
@property
def mode(self):
    # Remove 'b' from underlying buffer mode as this is a text wrapper
    return self.buffer.mode.replace('b', '')
```

## Testing
- Verified that before the fix, accessing `mode` returns `rb+` and writing bytes raises TypeError
- Verified that after the fix, accessing `mode` returns `r+` and writing strings works correctly
- All other file attributes continue to work as before via the existing `__getattr__` forwarding
