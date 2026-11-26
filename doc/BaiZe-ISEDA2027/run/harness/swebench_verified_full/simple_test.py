import copy
import sys
import os

# Add the django directory to path
sys.path.insert(0, os.path.abspath('django'))

# Import just the fields module directly, no need to setup Django
from django.forms.fields import Field, CharField, ChoiceField

print("Testing Field deepcopy error messages fix...")

# Test 1: Base Field
f1 = Field(error_messages={'required': 'Original msg'})
f2 = copy.deepcopy(f1)

f2.error_messages['required'] = 'Modified msg'
f2.error_messages['new'] = 'New msg'

print(f"Test 1 (Base Field):")
print(f"f1['required']: {f1.error_messages['required']}")
print(f"f2['required']: {f2.error_messages['required']}")
print(f"f1 has 'new'? {'new' in f1.error_messages}")
print(f"f2 has 'new'? {'new' in f2.error_messages}")
assert f1.error_messages['required'] == 'Original msg'
assert f2.error_messages['required'] == 'Modified msg'
assert 'new' not in f1.error_messages
assert 'new' in f2.error_messages
print("✅ Test 1 passed\n")

# Test 2: CharField (subclass)
c1 = CharField(max_length=10, error_messages={'min_length': 'Too short'})
c2 = copy.deepcopy(c1)

c2.error_messages['min_length'] = 'Way too short'
c2.error_messages['max_length'] = 'Too long'

print(f"Test 2 (CharField):")
print(f"c1['min_length']: {c1.error_messages['min_length']}")
print(f"c2['min_length']: {c2.error_messages['min_length']}")
print(f"c1 has 'max_length'? {'max_length' in c1.error_messages}")
print(f"c2 has 'max_length'? {'max_length' in c2.error_messages}")
assert c1.error_messages['min_length'] == 'Too short'
assert c2.error_messages['min_length'] == 'Way too short'
assert 'max_length' not in c1.error_messages
assert 'max_length' in c2.error_messages
print("✅ Test 2 passed\n")

# Test 3: ChoiceField (subclass with custom __deepcopy__)
ch1 = ChoiceField(choices=[('a', 'A')], error_messages={'invalid_choice': 'Bad choice'})
ch2 = copy.deepcopy(ch1)

ch2.error_messages['invalid_choice'] = 'Really bad choice'
ch2.error_messages['custom_choice_error'] = 'Pick something valid'

print(f"Test 3 (ChoiceField):")
print(f"ch1['invalid_choice']: {ch1.error_messages['invalid_choice']}")
print(f"ch2['invalid_choice']: {ch2.error_messages['invalid_choice']}")
print(f"ch1 has 'custom_choice_error'? {'custom_choice_error' in ch1.error_messages}")
print(f"ch2 has 'custom_choice_error'? {'custom_choice_error' in ch2.error_messages}")
assert ch1.error_messages['invalid_choice'] == 'Bad choice'
assert ch2.error_messages['invalid_choice'] == 'Really bad choice'
assert 'custom_choice_error' not in ch1.error_messages
assert 'custom_choice_error' in ch2.error_messages
print("✅ Test 3 passed\n")

print("🎉 All tests passed! The fix correctly deepcopies error_messages.")
