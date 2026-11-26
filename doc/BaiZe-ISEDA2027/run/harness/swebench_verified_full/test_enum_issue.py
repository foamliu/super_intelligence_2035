import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django'))

import enum
from django.db import models
from django.utils.translation import gettext_lazy as _

class MyChoice(models.TextChoices):
    FIRST_CHOICE = "first", _("The first choice, it is")
    SECOND_CHOICE = "second", _("The second choice, it is")

class MyObject(models.Model):
    my_str_value = models.CharField(max_length=10, choices=MyChoice.choices)
    
    class Meta:
        app_label = 'test'

# Test the issue
obj = MyObject(my_str_value=MyChoice.FIRST_CHOICE)
print(f"Type of my_str_value: {type(obj.my_str_value)}")
print(f"Value: {obj.my_str_value}")
print(f"str(value): {str(obj.my_str_value)}")
print(f"Is instance of str? {isinstance(obj.my_str_value, str)}")
print(f"Expected: 'first', Got: '{str(obj.my_str_value)}'")

# Now check what get_prep_value returns
field = MyObject._meta.get_field('my_str_value')
prepped = field.get_prep_value(MyChoice.FIRST_CHOICE)
print(f"\nget_prep_value returns: {prepped}, type: {type(prepped)}")
