#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple test to verify the unicode method fix works"""
import sys
import os
sys.path.insert(0, '/tmp/requests')

import requests

def test_unicode_method():
    print("Testing fix for unicode HTTP method...")
    
    # Test with unicode method
    req = requests.Request(method=u'POST', url=u'http://httpbin.org/post')
    prep = req.prepare()
    
    print(f"Method after preparation: {repr(prep.method)}")
    
    if sys.version_info[0] == 2:
        assert isinstance(prep.method, str), "Method should be bytes (str type) in Python 2"
        assert prep.method == 'POST', "Method should be 'POST'"
        print("✓ Method correctly converted to byte string in Python 2")
    else:
        assert isinstance(prep.method, str), "Method should be str type in Python 3"
        assert prep.method == 'POST', "Method should be 'POST'"
        print("✓ Method remains str type in Python 3")
        
    # Test with regular str method
    req2 = requests.Request(method='POST', url=u'http://httpbin.org/post')
    prep2 = req2.prepare()
    assert prep2.method == 'POST', "Regular str method should work"
    print("✓ Regular str method 'POST' works correctly")
    
    # Test with lowercase unicode method
    req3 = requests.Request(method=u'post', url=u'http://httpbin.org/post')
    prep3 = req3.prepare()
    assert prep3.method == 'POST', "Lowercase unicode method should be uppercased correctly"
    print("✓ Lowercase unicode method u'post' correctly converted to 'POST'")
    
    # Test with other unicode methods
    methods = [u'GET', u'PUT', u'DELETE', u'PATCH', u'OPTIONS', u'HEAD']
    for method in methods:
        req = requests.Request(method=method, url=u'http://httpbin.org/post')
        prep = req.prepare()
        assert prep.method == method.upper(), f"Method {repr(method)} should be correctly processed"
    print(f"✓ All unicode methods ({', '.join(methods)}) work correctly")
    
    print("\n✅ All tests passed! The fix works correctly.")
    print("\nThe fix ensures that unicode HTTP methods are encoded to byte strings")
    print("in Python 2, preventing the UnicodeDecodeError that occurs when")
    print("combining unicode headers/methods with byte string message bodies.")

if __name__ == "__main__":
    test_unicode_method()
