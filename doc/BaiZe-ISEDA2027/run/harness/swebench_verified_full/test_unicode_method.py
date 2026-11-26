#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests

# Test case from the issue
print("Testing with str method 'POST'...")
files = {u'file': open(u'/usr/bin/diff', u'rb')}
response = requests.request(method='POST', url=u'http://httpbin.org/post', files=files)
print(f"Success! Status code: {response.status_code}")

print("\nTesting with unicode method u'POST'...")
try:
    files = {u'file': open(u'/usr/bin/diff', u'rb')}
    response = requests.request(method=u'POST', url=u'http://httpbin.org/post', files=files)
    print(f"Success! Status code: {response.status_code}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
