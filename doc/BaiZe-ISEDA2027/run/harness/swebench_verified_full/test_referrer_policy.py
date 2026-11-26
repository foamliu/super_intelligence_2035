#!/usr/bin/env python3
"""Test that SECURE_REFERRER_POLICY setting works correctly."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django'))

from django.conf import settings
from django.http import HttpResponse
from django.middleware.security import SecurityMiddleware

# Test default setting
settings.configure(
    DEBUG=True,
    SECURE_REFERRER_POLICY='same-origin',
)

# Create middleware instance
middleware = SecurityMiddleware(lambda request: HttpResponse())

# Mock request
class MockRequest:
    def is_secure(self):
        return False

request = MockRequest()

# Process response
response = middleware.process_response(request, HttpResponse())

print("Testing default SECURE_REFERRER_POLICY='same-origin':")
print(f"Referrer-Policy header: {response.get('Referrer-Policy')}")
assert response.get('Referrer-Policy') == 'same-origin', f"Expected 'same-origin', got {response.get('Referrer-Policy')}"
print("✓ Default setting works correctly\n")

# Test custom setting
settings.configure(
    DEBUG=True,
    SECURE_REFERRER_POLICY='strict-origin-when-cross-origin',
)

middleware = SecurityMiddleware(lambda request: HttpResponse())
response = middleware.process_response(request, HttpResponse())

print("Testing custom SECURE_REFERRER_POLICY='strict-origin-when-cross-origin':")
print(f"Referrer-Policy header: {response.get('Referrer-Policy')}")
assert response.get('Referrer-Policy') == 'strict-origin-when-cross-origin', f"Expected 'strict-origin-when-cross-origin', got {response.get('Referrer-Policy')}"
print("✓ Custom setting works correctly\n")

# Test disabled setting
settings.configure(
    DEBUG=True,
    SECURE_REFERRER_POLICY=None,
)

middleware = SecurityMiddleware(lambda request: HttpResponse())
response = middleware.process_response(request, HttpResponse())

print("Testing SECURE_REFERRER_POLICY=None:")
print(f"Referrer-Policy header: {response.get('Referrer-Policy')}")
assert response.get('Referrer-Policy') is None, f"Expected None, got {response.get('Referrer-Policy')}"
print("✓ Disabled setting works correctly\n")

# Test that existing header is not overridden
settings.configure(
    DEBUG=True,
    SECURE_REFERRER_POLICY='same-origin',
)

middleware = SecurityMiddleware(lambda request: HttpResponse())
response = HttpResponse()
response['Referrer-Policy'] = 'no-referrer'
response = middleware.process_response(request, response)

print("Testing existing Referrer-Policy header is preserved:")
print(f"Referrer-Policy header: {response.get('Referrer-Policy')}")
assert response.get('Referrer-Policy') == 'no-referrer', f"Expected existing 'no-referrer' to be preserved, got {response.get('Referrer-Policy')}"
print("✓ Existing header is preserved correctly\n")

print("All tests passed! 🎉")
