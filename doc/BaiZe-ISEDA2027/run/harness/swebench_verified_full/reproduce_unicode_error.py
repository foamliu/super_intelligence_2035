import sys
import requests

print(f"Python version: {sys.version}")
print(f"Requests version: {requests.__version__}")

try:
    requests.get("http://.example.com")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
