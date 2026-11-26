import django
from django.conf import settings

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        INSTALLED_APPS=[],
    )
    django.setup()

from django.forms import (
    Form,
    CharField,
    MultiValueField,
    MultiWidget,
)

class MF(MultiValueField):
    widget = MultiWidget
    def __init__(self):
        fields = [
            CharField(required=False),
            CharField(required=True),
        ]
        widget = self.widget(widgets=[
            f.widget
            for f in fields
        ], attrs={})
        super(MF, self).__init__(
            fields=fields,
            widget=widget,
            require_all_fields=False,
            required=False,
        )
    def compress(self, value):
        return []

class F(Form):
    mf = MF()

# Test case 1: both subfields empty
f = F({
    'mf_0': '',
    'mf_1': '',
})
print("Test 1 - both empty: is_valid() =", f.is_valid())
print("Errors:", f.errors)
assert f.is_valid() == False, "Expected is_valid() to be False when required subfield is empty"
print("✓ Test 1 passed: correctly returns False when required subfield is empty")

# Test case 2: only optional subfield filled
f = F({
    'mf_0': 'xxx',
    'mf_1': '',
})
print("\nTest 2 - optional filled, required empty: is_valid() =", f.is_valid())
print("Errors:", f.errors)
assert f.is_valid() == False, "Expected is_valid() to be False when required subfield is empty"
print("✓ Test 2 passed: correctly returns False when required subfield is empty")

# Test case 3: both filled
f = F({
    'mf_0': 'xxx',
    'mf_1': 'yyy',
})
print("\nTest 3 - both filled: is_valid() =", f.is_valid())
print("Errors:", f.errors)
assert f.is_valid() == True, "Expected is_valid() to be True when all required subfields are filled"
print("✓ Test 3 passed: correctly returns True when all required subfields are filled")

# Test case 4: no required subfields, all empty should be valid
class MF2(MultiValueField):
    widget = MultiWidget
    def __init__(self):
        fields = [
            CharField(required=False),
            CharField(required=False),
        ]
        widget = self.widget(widgets=[f.widget for f in fields], attrs={})
        super().__init__(
            fields=fields,
            widget=widget,
            require_all_fields=False,
            required=False,
        )
    def compress(self, value):
        return []

class F2(Form):
    mf = MF2()

f2 = F2({'mf_0': '', 'mf_1': ''})
print("\nTest 4 - no required subfields, both empty: is_valid() =", f2.is_valid())
print("Errors:", f2.errors)
assert f2.is_valid() == True, "Expected is_valid() to be True when no required subfields and all empty"
print("✓ Test 4 passed: correctly returns True when no required subfields and all empty")

# Test case 5: require_all_fields=True, parent required=False, all empty should be valid
class MF3(MultiValueField):
    widget = MultiWidget
    def __init__(self):
        fields = [
            CharField(required=True),
            CharField(required=True),
        ]
        widget = self.widget(widgets=[f.widget for f in fields], attrs={})
        super().__init__(
            fields=fields,
            widget=widget,
            require_all_fields=True,
            required=False,
        )
    def compress(self, value):
        return []

class F3(Form):
    mf = MF3()

f3 = F3({'mf_0': '', 'mf_1': ''})
print("\nTest 5 - require_all_fields=True, parent required=False, all empty: is_valid() =", f3.is_valid())
print("Errors:", f3.errors)
assert f3.is_valid() == True, "Expected is_valid() to be True when require_all_fields=True and parent required=False and all empty"
print("✓ Test 5 passed: correctly returns True for require_all_fields=True case")

print("\n✅ All tests passed!")
