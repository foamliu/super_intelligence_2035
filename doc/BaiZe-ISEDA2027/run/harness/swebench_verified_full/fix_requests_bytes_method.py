"""
Fix for the requests bytes method issue: when a bytes method like b'GET' is passed,
it was being converted to the string "b'GET'" instead of "GET".

This bug was present in requests 2.4.3 and older versions.
"""
import sys

def fix_requests_prepare_method():
    """Patch requests to handle bytes method correctly"""
    import requests
    from requests.models import PreparedRequest
    from requests._internal_utils import to_native_string
    
    original_prepare_method = PreparedRequest.prepare_method
    
    def patched_prepare_method(self, method):
        self.method = method
        if self.method is not None:
            # Handle bytes method correctly by decoding it
            if isinstance(self.method, bytes):
                self.method = self.method.decode('utf-8')
            self.method = to_native_string(self.method.upper())
    
    PreparedRequest.prepare_method = patched_prepare_method
    print(f"Patched requests {requests.__version__} to handle bytes HTTP methods correctly")

# Test the fix
if __name__ == "__main__":
    import requests
    
    print(f"Python version: {sys.version}")
    print(f"Requests version: {requests.__version__}")
    
    # Test without patch first
    print("\nTesting without patch:")
    try:
        # Create a prepared request with bytes method
        req = requests.Request(b'GET', 'https://httpbin.org/get')
        prep = req.prepare()
        print(f"Method without patch: {repr(prep.method)}")
        if prep.method == "GET":
            print("✓ Already fixed in this version of requests")
        else:
            print(f"✗ Bug present: method is {repr(prep.method)}, should be 'GET'")
    except Exception as e:
        print(f"Error: {e}")
    
    # Apply patch
    fix_requests_prepare_method()
    
    # Test with patch
    print("\nTesting with patch:")
    try:
        req = requests.Request(b'GET', 'https://httpbin.org/get')
        prep = req.prepare()
        print(f"Method with patch: {repr(prep.method)}")
        assert prep.method == "GET", f"Expected 'GET', got {repr(prep.method)}"
        print("✓ Patch works correctly")
        
        # Test other methods
        for method in [b'POST', b'PUT', b'DELETE', b'PATCH', b'OPTIONS', b'HEAD']:
            req = requests.Request(method, 'https://httpbin.org/get')
            prep = req.prepare()
            assert prep.method == method.decode('utf-8').upper(), f"Expected {method.decode().upper()}, got {repr(prep.method)}"
        print("✓ All HTTP methods work correctly with bytes input")
        
    except Exception as e:
        print(f"Error: {e}")
