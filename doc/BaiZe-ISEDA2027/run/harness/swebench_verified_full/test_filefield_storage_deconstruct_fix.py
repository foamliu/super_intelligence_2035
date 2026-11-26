
"""
Test for FileField storage callable deconstruct fix.
This test verifies that when a FileField has a callable storage that returns default_storage,
it is always included in the deconstructed kwargs, preventing random migration changes.
"""
from django.core.files.storage import FileSystemStorage, default_storage
from django.db import models
import random

# Create a callable storage that sometimes returns default_storage
other_storage = FileSystemStorage(location='/media/other')

def get_storage():
    return random.choice([default_storage, other_storage])

# Test 1: FileField with callable storage
field = models.FileField(storage=get_storage)
name, path, args, kwargs = field.deconstruct()

# Verify that storage is always present in kwargs
assert 'storage' in kwargs, "storage should be present in deconstructed kwargs"
assert kwargs['storage'] is get_storage, "storage should be the original callable"

# Test multiple times to ensure it's not random
for _ in range(10):
    # Access storage to trigger evaluation (may return default_storage)
    _ = field.storage
    name, path, args, kwargs = field.deconstruct()
    assert 'storage' in kwargs, f"storage should be present (iteration {_})"
    assert kwargs['storage'] is get_storage, f"storage should be the callable (iteration {_})"

# Test 2: FileField with default storage (no storage argument)
field_default = models.FileField()
name, path, args, kwargs = field_default.deconstruct()
assert 'storage' not in kwargs, "storage should not be present for default storage"

# Test 3: FileField with explicit default_storage
field_explicit_default = models.FileField(storage=default_storage)
name, path, args, kwargs = field_explicit_default.deconstruct()
assert 'storage' not in kwargs, "storage should not be present when explicitly passing default_storage"

# Test 4: FileField with non-callable custom storage
field_custom = models.FileField(storage=other_storage)
name, path, args, kwargs = field_custom.deconstruct()
assert 'storage' in kwargs, "storage should be present for custom non-callable storage"
assert kwargs['storage'] is other_storage, "storage should be the custom storage instance"

print("✅ All tests passed! The fix works correctly.")
