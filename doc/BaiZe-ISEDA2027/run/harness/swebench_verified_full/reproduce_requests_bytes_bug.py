import requests

# Test case from the issue
print("Testing PUT request with binary payload...")
try:
    response = requests.put("http://httpbin.org/put", data=u"ööö".encode("utf-8"))
    print(f"Success! Status code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error occurred: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
