
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django'))

from django.conf import settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ]
    )

import django
django.setup()

from django.db import models
from django.template import Template, Context

# Define the choices enum
class YearInSchool(models.TextChoices):
    FRESHMAN = 'FR', 'Freshman'
    SOPHOMORE = 'SO', 'Sophomore'
    JUNIOR = 'JR', 'Junior'
    SENIOR = 'SR', 'Senior'

# Create a test model
class Student(models.Model):
    name = models.CharField(max_length=100)
    year_in_school = models.CharField(max_length=2, choices=YearInSchool.choices)
    
    class Meta:
        app_label = 'test'

# Test the template issue
print("Testing template enum usage...")

# Create a student instance
student = Student(name='John Doe', year_in_school=YearInSchool.FRESHMAN)

# Render the template
template = Template("""
{% if student.year_in_school == YearInSchool.FRESHMAN %}
    John is a freshman!
{% else %}
    John is not a freshman.
{% endif %}
""")

context = Context({
    'student': student,
    'YearInSchool': YearInSchool,
})

output = template.render(context).strip()
print(f"Template output: {repr(output)}")

assert output == "John is a freshman!", f"Expected 'John is a freshman!', got {repr(output)}"
print("✅ Test passed! Enums work correctly in templates now.")

# Test that the enum is not called
print("\nTesting that enum class is not called in templates...")
template2 = Template("{{ YearInSchool }}")
context2 = Context({'YearInSchool': YearInSchool})
output2 = template2.render(context2)
print(f"Template output for YearInSchool: {repr(output2)}")
# Should output the class representation, not try to call it
assert "YearInSchool" in output2
print("✅ Enum class is correctly not called in templates.")
