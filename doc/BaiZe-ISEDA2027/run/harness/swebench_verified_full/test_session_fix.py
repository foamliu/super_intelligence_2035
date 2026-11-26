import os
import sys
import django
from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase

# Configure settings
settings.configure(
    SECRET_KEY='test-secret-key',
    SESSION_SERIALIZER='django.contrib.sessions.serializers.JSONSerializer',
)
django.setup()

# Test 1: DEFAULT_HASHING_ALGORITHM not set (default), should use new format
print("Test 1: No DEFAULT_HASHING_ALGORITHM set, using new format")
session = SessionBase()
data = {'test_key': 'test_value'}
encoded_new = session.encode(data)
print(f"Encoded (new format): {encoded_new}")
decoded = session.decode(encoded_new)
print(f"Decoded: {decoded}")
assert decoded == data, "Decoding failed for new format"

# Test 2: Set DEFAULT_HASHING_ALGORITHM to 'sha1', should use legacy format
print("\nTest 2: DEFAULT_HASHING_ALGORITHM = 'sha1', using legacy format")
settings.DEFAULT_HASHING_ALGORITHM = 'sha1'
encoded_legacy = session.encode(data)
print(f"Encoded (legacy format): {encoded_legacy}")
decoded = session.decode(encoded_legacy)
print(f"Decoded: {decoded}")
assert decoded == data, "Decoding failed for legacy format"

# Test 3: Verify legacy format is compatible with old decode logic
print("\nTest 3: Verify legacy format is compatible with old decode")
import base64
from django.utils.crypto import constant_time_compare
encoded_data = base64.b64decode(encoded_legacy.encode('ascii'))
hash, serialized = encoded_data.split(b':', 1)
expected_hash = session._hash(serialized)
assert constant_time_compare(hash.decode(), expected_hash), "Legacy hash mismatch"
print("Legacy format hash matches, old versions can decode this")

print("\nAll tests passed! Fix works correctly.")
