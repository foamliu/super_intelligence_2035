import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django'))

from django import forms
from django.contrib.postgres.forms.array import SplitArrayField, SplitArrayWidget

class TestForm(forms.Form):
    bool_array = SplitArrayField(
        base_field=forms.BooleanField(required=False),
        size=3,
        required=False
    )

# Test with initial value [True, False, True]
form = TestForm(initial={'bool_array': [True, False, True]})
html = form.as_p()
print(html)
print("\n--- Checking checkboxes ---")
lines = html.split('\n')
checked_count = 0
for line in lines:
    if 'type="checkbox"' in line:
        print(line.strip())
        if 'checked' in line:
            checked_count +=1

print(f"\nTotal checked checkboxes: {checked_count} (expected 2)")
print(f"Test {'PASSED' if checked_count == 2 else 'FAILED'}")
