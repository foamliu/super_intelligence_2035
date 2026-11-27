import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from django.conf import settings
if not settings.configured:
    settings.configure(
        SECRET_KEY='test-secret-key',
        SESSION_SERIALIZER='django.contrib.sessions.serializers.JSONSerializer',
    )

from django.contrib.sessions.backends.base import SessionBase

# Test 1: DEFAULT_HASHING_ALGORITHM not set (default), should use new format
print("Test 1: No DEFAULT_HASHING_ALGORITHM set, using new format")
session = SessionBase()
test_data = {'foo': 'bar', 'test': 123}
encoded = session.encode(test_data)
print(f"Encoded (new format): {encoded[:50]}...")
decoded = session.decode(encoded)
print(f"Decoded correctly: {decoded == test_data}")
print(f"Is legacy format (contains ':')? {':' in encoded}")

# Test 2: Set DEFAULT_HASHING_ALGORITHM to 'sha1', should use legacy format
print("\nTest 2: DEFAULT_HASHING_ALGORITHM = 'sha1', using legacy format")
settings.DEFAULT_HASHING_ALGORITHM = 'sha1'
encoded_legacy = session.encode(test_data)
print(f"Encoded (legacy format): {encoded_legacy}")
decoded_legacy = session.decode(encoded_legacy)
print(f"Decoded correctly: {decoded_legacy == test_data}")
print(f"Is legacy format (contains ':')? {':' in encoded_legacy}")

# Test 3: Legacy format is compatible with old decode function
print("\nTest 3: Legacy format compatibility with old decode logic")
import base64
from django.utils.crypto import constant_time_compare

def old_decode(session_data):
    encoded_data = base64.b64decode(session_data.encode('ascii'))
    hash, serialized = encoded_data.split(b':', 1)
    expected_hash = session._hash(serialized)
    if not constant_time_compare(hash.decode(), expected_hash):
        raise Exception("Invalid hash")
    return session.serializer().loads(serialized)

old_decoded = old_decode(encoded_legacy)
print(f"Old decode works with legacy format: {old_decoded == test_data}")
