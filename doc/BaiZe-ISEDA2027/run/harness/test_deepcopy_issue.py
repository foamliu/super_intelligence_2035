import copy
from django import forms
from django.forms.fields import CharField

# Test case 1: Test field deepcopy
field1 = CharField(error_messages={'required': 'Original required message'})
field2 = copy.deepcopy(field1)

# Modify field2's error messages
field2.error_messages['required'] = 'Modified required message'
field2.error_messages['custom'] = 'Custom error message'

print("Test 1: Field deepcopy")
print(f"field1 error messages: {field1.error_messages}")
print(f"field2 error messages: {field2.error_messages}")
print(f"Are they the same dict? {field1.error_messages is field2.error_messages}")
print(f"Expected: field1 should have original message, field2 modified.")
print(f"Result: {'PASS' if field1.error_messages['required'] == 'Original required message' and field2.error_messages['required'] == 'Modified required message' else 'FAIL'}")
print()

# Test case 2: Test form instance field isolation
class TestForm(forms.Form):
    name = CharField(error_messages={'required': 'Form original required message'})

form1 = TestForm()
form2 = TestForm()

# Modify form1's field error messages
form1.fields['name'].error_messages['required'] = 'Form1 modified required message'
form1.fields['name'].error_messages['custom_form'] = 'Custom form error'

print("Test 2: Form instance field isolation")
print(f"form1 field error messages: {form1.fields['name'].error_messages}")
print(f"form2 field error messages: {form2.fields['name'].error_messages}")
print(f"Are they the same dict? {form1.fields['name'].error_messages is form2.fields['name'].error_messages}")
print(f"Expected: form1 should have modified message, form2 original.")
print(f"Result: {'PASS' if form1.fields['name'].error_messages['required'] == 'Form1 modified required message' and form2.fields['name'].error_messages['required'] == 'Form original required message' else 'FAIL'}")
