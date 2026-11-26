import copy
from django.forms import CharField, Form

def test_field_deepcopy_error_messages():
    print("Testing Form Field deepcopy error messages fix...")
    
    # Test 1: Direct field deepcopy
    field1 = CharField(error_messages={'required': 'Original required message'})
    field2 = copy.deepcopy(field1)
    
    # Modify field2's error messages
    field2.error_messages['required'] = 'Modified required message'
    field2.error_messages['custom'] = 'Custom error message'
    
    print(f"Test 1 - Direct field deepcopy:")
    print(f"field1 error_messages['required']: {field1.error_messages['required']}")
    print(f"field2 error_messages['required']: {field2.error_messages['required']}")
    print(f"'custom' in field1.error_messages: {'custom' in field1.error_messages}")
    print(f"'custom' in field2.error_messages: {'custom' in field2.error_messages}")
    
    # Verify they are separate
    assert field1.error_messages['required'] == 'Original required message', "field1's required message should not change"
    assert field2.error_messages['required'] == 'Modified required message', "field2's required message should be modified"
    assert 'custom' not in field1.error_messages, "field1 should not have custom error message"
    assert 'custom' in field2.error_messages, "field2 should have custom error message"
    print("✅ Test 1 passed!\n")
    
    # Test 2: Form instance field deepcopy (the actual use case mentioned in the issue)
    class TestForm(Form):
        name = CharField(error_messages={'required': 'Name is required'})
    
    form1 = TestForm()
    form2 = TestForm()
    
    # Modify form1's field error messages
    form1.fields['name'].error_messages['required'] = 'Name is mandatory for form1'
    form1.fields['name'].error_messages['min_length'] = 'Name is too short'
    
    print(f"Test 2 - Form instance fields:")
    print(f"form1 name field required message: {form1.fields['name'].error_messages['required']}")
    print(f"form2 name field required message: {form2.fields['name'].error_messages['required']}")
    print(f"'min_length' in form1.fields['name'].error_messages: {'min_length' in form1.fields['name'].error_messages}")
    print(f"'min_length' in form2.fields['name'].error_messages: {'min_length' in form2.fields['name'].error_messages}")
    
    # Verify they are separate
    assert form1.fields['name'].error_messages['required'] == 'Name is mandatory for form1', "form1's field should have modified message"
    assert form2.fields['name'].error_messages['required'] == 'Name is required', "form2's field should have original message"
    assert 'min_length' in form1.fields['name'].error_messages, "form1 should have min_length error"
    assert 'min_length' not in form2.fields['name'].error_messages, "form2 should not have min_length error"
    print("✅ Test 2 passed!\n")
    
    # Test 3: ChoiceField (subclass with own __deepcopy__)
    from django.forms import ChoiceField
    choice_field1 = ChoiceField(choices=[('a', 'A'), ('b', 'B')], error_messages={'invalid_choice': 'Original invalid choice'})
    choice_field2 = copy.deepcopy(choice_field1)
    
    choice_field2.error_messages['invalid_choice'] = 'Modified invalid choice'
    choice_field2.choices = [('c', 'C'), ('d', 'D')]
    
    print(f"Test 3 - ChoiceField (subclass with custom __deepcopy__):")
    print(f"choice_field1 invalid_choice message: {choice_field1.error_messages['invalid_choice']}")
    print(f"choice_field2 invalid_choice message: {choice_field2.error_messages['invalid_choice']}")
    print(f"choice_field1 choices: {choice_field1.choices}")
    print(f"choice_field2 choices: {choice_field2.choices}")
    
    assert choice_field1.error_messages['invalid_choice'] == 'Original invalid choice'
    assert choice_field2.error_messages['invalid_choice'] == 'Modified invalid choice'
    assert choice_field1.choices == [('a', 'A'), ('b', 'B')]
    assert choice_field2.choices == [('c', 'C'), ('d', 'D')]
    print("✅ Test 3 passed!\n")
    
    print("🎉 All tests passed! The fix works correctly.")

if __name__ == '__main__':
    import os
    import sys
    sys.path.insert(0, os.path.abspath('django'))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django.conf.global_settings')
    import django
    django.setup()
    test_field_deepcopy_error_messages()
