#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test to verify the unicode method fix works in Python 2.7"""
import sys
import os
sys.path.insert(0, '/tmp/requests')

import requests

def test_unicode_method():
    print("Testing fix for unicode HTTP method...")
    
    # Test with unicode method
    files = {u'file': open(u'/usr/bin/diff', u'rb')}
    
    # This used to raise UnicodeDecodeError, now should work
    try:
        # We'll use a mock URL to avoid actual network call
        from mock import Mock, patch
        with patch('requests.adapters.HTTPAdapter.send') as mock_send:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.raw = Mock()
            mock_resp.headers = {}
            mock_resp.elapsed = 0
            mock_resp.history = []
            mock_send.return_value = mock_resp
            
            response = requests.request(method=u'POST', url=u'http://httpbin.org/post', files=files)
            print("✓ Success! Unicode method u'POST' works without UnicodeDecodeError")
            
            # Verify the method was converted to bytes
            req = requests.Request(method=u'POST', url=u'http://httpbin.org/post', files=files)
            prep = req.prepare()
            
            if sys.version_info[0] == 2:
                assert isinstance(prep.method, str), "Method should be bytes (str type) in Python 2"
                assert prep.method == 'POST', "Method should be 'POST'"
                print("✓ Method correctly converted to byte string in Python 2")
            else:
                assert isinstance(prep.method, str), "Method should be str type in Python 3"
                assert prep.method == 'POST', "Method should be 'POST'"
                print("✓ Method remains str type in Python 3")
                
    except ImportError:
        # Mock not available, just test that no error is raised when preparing the request
        print("⚠️  Mock not available, testing request preparation only...")
        session = requests.Session()
        req = requests.Request(method=u'POST', url=u'http://httpbin.org/post', files=files)
        prep = session.prepare_request(req)
        print("✓ Request preparation with unicode method succeeds")
        
        if sys.version_info[0] == 2:
            assert isinstance(prep.method, str), "Method should be bytes (str type) in Python 2"
            assert prep.method == 'POST', "Method should be 'POST'"
            print("✓ Method correctly converted to byte string in Python 2")
        else:
            assert isinstance(prep.method, str), "Method should be str type in Python 3"
            assert prep.method == 'POST', "Method should be 'POST'"
            print("✓ Method remains str type in Python 3")
            
    # Test with regular str method still works
    req2 = requests.Request(method='POST', url=u'http://httpbin.org/post', files=files)
    prep2 = req2.prepare()
    assert prep2.method == 'POST', "Regular str method should still work"
    print("✓ Regular str method 'POST' continues to work")
    
    print("\nAll tests passed! The fix works correctly.")

if __name__ == "__main__":
    test_unicode_method()
