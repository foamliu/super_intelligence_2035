
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django'))

# Import directly to avoid circular import
from django.db.models.enums import Choices, IntegerChoices, TextChoices, ChoicesMeta

print("Checking do_not_call_in_templates attribute...")

# Check that the metaclass has the attribute
assert hasattr(ChoicesMeta, 'do_not_call_in_templates'), "ChoicesMeta missing do_not_call_in_templates"
assert ChoicesMeta.do_not_call_in_templates == True, "ChoicesMeta.do_not_call_in_templates should be True"
print("✅ ChoicesMeta has do_not_call_in_templates = True")

# Check that all base classes inherit it
assert hasattr(Choices, 'do_not_call_in_templates'), "Choices missing do_not_call_in_templates"
assert Choices.do_not_call_in_templates == True, "Choices.do_not_call_in_templates should be True"
print("✅ Choices has do_not_call_in_templates = True")

assert hasattr(IntegerChoices, 'do_not_call_in_templates'), "IntegerChoices missing do_not_call_in_templates"
assert IntegerChoices.do_not_call_in_templates == True, "IntegerChoices.do_not_call_in_templates should be True"
print("✅ IntegerChoices has do_not_call_in_templates = True")

assert hasattr(TextChoices, 'do_not_call_in_templates'), "TextChoices missing do_not_call_in_templates"
assert TextChoices.do_not_call_in_templates == True, "TextChoices.do_not_call_in_templates should be True"
print("✅ TextChoices has do_not_call_in_templates = True")

# Test a custom subclass
class YearInSchool(TextChoices):
    FRESHMAN = 'FR', 'Freshman'
    SOPHOMORE = 'SO', 'Sophomore'

assert hasattr(YearInSchool, 'do_not_call_in_templates'), "YearInSchool subclass missing do_not_call_in_templates"
assert YearInSchool.do_not_call_in_templates == True, "YearInSchool.do_not_call_in_templates should be True"
print("✅ Custom TextChoices subclass inherits do_not_call_in_templates = True")

print("\nAll checks passed! The fix is working correctly.")
print("\nSummary:")
print("- Added Choices, IntegerChoices, TextChoices classes in django/db/models/enums.py")
print("- Added do_not_call_in_templates = True to ChoicesMeta metaclass, so all Choices subclasses inherit it")
print("- This prevents Django templates from trying to call the Choices classes when they are used in templates")
print("- Fixes the issue where {% if student.year_in_school == YearInSchool.FRESHMAN %} would fail")
