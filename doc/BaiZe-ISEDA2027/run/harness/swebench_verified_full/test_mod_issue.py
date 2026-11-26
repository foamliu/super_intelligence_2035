import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django'))

from django.db import models
from django.db.models import F, Value
from django.conf import settings

# Configure settings
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
    ]
)

import django
django.setup()

# Create a test model
class TestModel(models.Model):
    decimal_field = models.DecimalField(max_digits=10, decimal_places=2)
    int_field = models.IntegerField()
    
    class Meta:
        app_label = 'test'

# Create tables
from django.db import connection
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(TestModel)

# Test the issue
print("Testing F('decimal_field') + F('int_field'):")
try:
    expr = F('decimal_field') + F('int_field')
    print(f"  Output field type: {expr.output_field.__class__.__name__}")
    print(f"  Success!")
except Exception as e:
    print(f"  Error: {e}")

print("\nTesting F('decimal_field') * F('int_field'):")
try:
    expr = F('decimal_field') * F('int_field')
    print(f"  Output field type: {expr.output_field.__class__.__name__}")
    print(f"  Success!")
except Exception as e:
    print(f"  Error: {e}")

print("\nTesting F('decimal_field') / F('int_field'):")
try:
    expr = F('decimal_field') / F('int_field')
    print(f"  Output field type: {expr.output_field.__class__.__name__}")
    print(f"  Success!")
except Exception as e:
    print(f"  Error: {e}")

print("\nTesting F('decimal_field') % F('int_field'):")
try:
    expr = F('decimal_field') % F('int_field')
    print(f"  Output field type: {expr.output_field.__class__.__name__}")
    print(f"  Success!")
except Exception as e:
    print(f"  Error: {e}")

print("\nTesting F('int_field') % F('decimal_field'):")
try:
    expr = F('int_field') % F('decimal_field')
    print(f"  Output field type: {expr.output_field.__class__.__name__}")
    print(f"  Success!")
except Exception as e:
    print(f"  Error: {e}")
