import sys
import os

# Add the django directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django'))

from django import forms
from django.conf import settings

# Configure minimal Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        INSTALLED_APPS=[],
        USE_I18N=False,
    )
    import django
    django.setup()


def test_checkbox_select_multiple_custom_id():
    """Test that BoundWidget.id_for_label uses the id set in attrs, not generated one."""
    class TestForm(forms.Form):
        choices = [('1', 'Choice 1'), ('2', 'Choice 2'), ('3', 'Choice 3')]
        my_field = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple(attrs={'id': 'custom-id'}),
            choices=choices
        )
    
    form = TestForm()
    # Get the subwidgets
    widgets = list(form['my_field'])
    
    # Check that each widget's id_for_label matches the expected custom id with index
    expected_ids = ['custom-id_0', 'custom-id_1', 'custom-id_2']
    all_pass = True
    for i, widget in enumerate(widgets):
        if widget.id_for_label != expected_ids[i]:
            print(f"FAIL test_checkbox_select_multiple_custom_id: Expected {expected_ids[i]}, got {widget.id_for_label}")
            all_pass = False
        # Also check that the tag has the correct id
        if f'id="{expected_ids[i]}"' not in widget.tag():
            print(f"FAIL test_checkbox_select_multiple_custom_id: Tag missing expected id {expected_ids[i]}")
            all_pass = False
    if all_pass:
        print("PASS test_checkbox_select_multiple_custom_id")
    return all_pass


def test_radio_select_custom_auto_id():
    """Test with custom auto_id format on form."""
    class TestForm(forms.Form):
        choices = [('a', 'Option A'), ('b', 'Option B')]
        radio = forms.ChoiceField(
            widget=forms.RadioSelect,
            choices=choices
        )
    
    # Set custom auto_id format
    form = TestForm(auto_id='my_form_%s')
    
    widgets = list(form['radio'])
    expected_ids = ['my_form_radio_0', 'my_form_radio_1']
    all_pass = True
    for i, widget in enumerate(widgets):
        if widget.id_for_label != expected_ids[i]:
            print(f"FAIL test_radio_select_custom_auto_id: Expected {expected_ids[i]}, got {widget.id_for_label}")
            all_pass = False
        if f'id="{expected_ids[i]}"' not in widget.tag():
            print(f"FAIL test_radio_select_custom_auto_id: Tag missing expected id {expected_ids[i]}")
            all_pass = False
        # Check that label for attribute matches
        label_tag = f'<label for="{expected_ids[i]}">'
        if label_tag not in widget.tag(wrap_label=True):
            print(f"FAIL test_radio_select_custom_auto_id: Label missing expected for attribute {expected_ids[i]}")
            all_pass = False
    if all_pass:
        print("PASS test_radio_select_custom_auto_id")
    return all_pass


def test_no_id_case():
    """Test that when no id is provided, falls back to original behavior."""
    class TestForm(forms.Form):
        choices = [('x', 'X'), ('y', 'Y')]
        field = forms.ChoiceField(
            widget=forms.RadioSelect,
            choices=choices
        )
    
    # Set auto_id to False so no id is generated
    form = TestForm(auto_id=False)
    
    widgets = list(form['field'])
    all_pass = True
    for i, widget in enumerate(widgets):
        expected = f'id_{widget.data["name"]}_{i}'
        if widget.id_for_label != expected:
            print(f"FAIL test_no_id_case: Expected {expected}, got {widget.id_for_label}")
            all_pass = False
    if all_pass:
        print("PASS test_no_id_case")
    return all_pass


if __name__ == "__main__":
    results = []
    results.append(test_checkbox_select_multiple_custom_id())
    results.append(test_radio_select_custom_auto_id())
    results.append(test_no_id_case())
    
    if all(results):
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print("\nSome tests failed!")
        sys.exit(1)
