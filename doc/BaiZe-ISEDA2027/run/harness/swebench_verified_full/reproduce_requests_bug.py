import sys
import requests

print(f"Python version: {sys.version}")
print(f"Requests version: {requests.__version__}")

# Test what happens when we pass bytes method
try:
    # This will fail with 404 if we send b'GET' as the method
    resp = requests.request(b'GET', 'https://httpbin.org/get')
    print(f"Response status: {resp.status_code}")
    print(f"Response content: {resp.text}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")

# Let's also look at how builtin_str is defined in requests
print("\nLooking at requests builtin_str definition:")
import inspect
from requests import sessions
print(inspect.getsource(sessions))
