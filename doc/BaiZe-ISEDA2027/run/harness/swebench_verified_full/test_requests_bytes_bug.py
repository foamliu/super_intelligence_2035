from requests.models import PreparedRequest
from requests._internal_utils import to_native_string

# Simulate the bug
print("Testing to_native_string with utf-8 bytes...")
data = u"ööö".encode("utf-8")
print(f"Data: {data!r}")
try:
    # This is what the buggy code was doing
    result = to_native_string(data)
    print(f"Result: {result!r}")
except UnicodeDecodeError as e:
    print(f"ERROR: {e}")
    print("This is exactly the bug! to_native_string tries to decode bytes as ASCII.")

print("\nTesting PreparedRequest with binary data...")
req = PreparedRequest()
req.prepare_method("PUT")
req.prepare_url("http://httpbin.org/put", params=None)
req.prepare_headers({})
try:
    req.prepare_body(data=data, files=None)
    print(f"Success! Body type: {type(req.body)}, value: {req.body!r}")
    print(f"Content-Length header: {req.headers.get('Content-Length')}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
