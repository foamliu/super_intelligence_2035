
import sys
import os

# Add the django directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django'))

# Import only what we need, avoid importing test modules that cause circular imports
from django.forms import CharField, MultiValueField, ValidationError

class MF(MultiValueField):
    def __init__(self):
        fields = [
            CharField(required=False),
            CharField(required=True),
        ]
        super().__init__(
            fields=fields,
            require_all_fields=False,
            required=False,
        )
    def compress(self, value):
        return []

# Test the clean method directly
field = MF()

print("Testing clean(['', '']):")
try:
    result = field.clean(['', ''])
    print(f"❌ FAILED: clean returned {result} instead of raising ValidationError")
except ValidationError:
    print(f"✅ PASSED: Got expected ValidationError")

print("\nTesting clean(['xxx', '']):")
try:
    result = field.clean(['xxx', ''])
    print(f"❌ FAILED: clean returned {result} instead of raising ValidationError")
except ValidationError:
    print(f"✅ PASSED: Got expected ValidationError")

print("\nTesting clean(['xxx', 'yyy']):")
try:
    result = field.clean(['xxx', 'yyy'])
    print(f"✅ PASSED: clean returned {result}")
except ValidationError as e:
    print(f"❌ FAILED: Unexpected ValidationError: {e.messages}")

# Test with no required subfields
class MF2(MultiValueField):
    def __init__(self):
        fields = [
            CharField(required=False),
            CharField(required=False),
        ]
        super().__init__(
            fields=fields,
            require_all_fields=False,
            required=False,
        )
    def compress(self, value):
        return []

field2 = MF2()
print("\nTesting no required subfields, clean(['', '']):")
try:
    result = field2.clean(['', ''])
    print(f"✅ PASSED: clean returned {result} (expected, no required fields)")
except ValidationError as e:
    print(f"❌ FAILED: Unexpected ValidationError: {e.messages}")

# Test require_all_fields=True
class MF3(MultiValueField):
    def __init__(self):
        fields = [
            CharField(required=True),
            CharField(required=True),
        ]
        super().__init__(
            fields=fields,
            require_all_fields=True,
            required=False,
        )
    def compress(self, value):
        return []

field3 = MF3()
print("\nTesting require_all_fields=True, clean(['', '']):")
try:
    result = field3.clean(['', ''])
    print(f"✅ PASSED: clean returned {result} (expected, parent not required)")
except ValidationError as e:
    print(f"❌ FAILED: Unexpected ValidationError: {e.messages}")
