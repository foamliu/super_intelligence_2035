import django
from django.db import models
from django.db.models.fields import CharField
from django.test import TestCase

# Setup Django
django.setup()

# Create a custom lookup
class CustomExact(models.lookups.Exact):
    lookup_name = 'custom_exact'

# Test the fix
print("Testing lookup unregister cache clearing...")

# Register the lookup
CharField.register_lookup(CustomExact)

# Check it exists
field = CharField()
lookup = field.get_lookup('custom_exact')
print(f"Lookup registered: {lookup is not None}")
assert lookup is CustomExact, "Lookup should be registered"

# Unregister the lookup
CharField._unregister_lookup(CustomExact)

# Check it no longer exists (this would fail before our fix)
lookup = field.get_lookup('custom_exact')
print(f"Lookup unregistered: {lookup is None}")
assert lookup is None, "Lookup should be unregistered and cache cleared"

print("All tests passed! Fix is working correctly.")
