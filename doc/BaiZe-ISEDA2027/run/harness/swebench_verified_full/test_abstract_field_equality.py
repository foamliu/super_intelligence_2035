import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django'))
import django
from django.conf import settings

# Setup Django settings
settings.configure(
    DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'django.contrib.auth',
    ],
)

django.setup()

from django.db import models
from django.db.models import IntegerField

# Test case from the issue
class A(models.Model):
    class Meta:
        abstract = True
    myfield = IntegerField()

class B(A):
    pass

class C(A):
    pass

# Get the fields
field_b = B._meta.get_field('myfield')
field_c = C._meta.get_field('myfield')

print(f"Field B creation counter: {field_b.creation_counter}")
print(f"Field C creation counter: {field_c.creation_counter}")
print(f"Field B model: {field_b.model}")
print(f"Field C model: {field_c.model}")
print(f"Are fields equal? {field_b == field_c}")
print(f"Length of set containing both fields: {len({field_b, field_c})}")

# Expected results after fix:
# Are fields equal? False
# Length of set containing both fields: 2

# Also test that fields from same model are equal
field_b2 = B._meta.get_field('myfield')
print(f"\nField B vs same field from B: {field_b == field_b2}")
print(f"Length of set containing same field twice: {len({field_b, field_b2})}")

# Test that fields with different creation counters are still unequal
field1 = IntegerField()
field2 = IntegerField()
print(f"\nTwo separate fields: {field1 == field2}")
print(f"Length of set with two separate fields: {len({field1, field2})}")
