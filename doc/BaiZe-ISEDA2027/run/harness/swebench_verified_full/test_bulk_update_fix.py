
import os
import sys
# The django source repo is in ./django directory, which contains the django module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django'))
import django
from django.db import models, connection
from django.conf import settings

# Configure Django settings
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

# Create test model
class SelfRef(models.Model):
    name = models.CharField(max_length=100)
    c8 = models.CharField(max_length=100)
    
    class Meta:
        app_label = 'test'

# Create tables
from django.db import connection
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(SelfRef)

# Test the fix
print("Testing bulk_update with F expression...")
obj = SelfRef.objects.create(name='test_name', c8='initial_value')
print(f"Initial obj: name={obj.name}, c8={obj.c8}")

# Assign F expression
obj.c8 = models.F('name')
# Bulk update
rows_updated = SelfRef.objects.bulk_update([obj], ['c8'])
print(f"Rows updated: {rows_updated}")

# Refresh from db
obj.refresh_from_db()
print(f"After bulk_update + refresh: c8={obj.c8}")

# Check the last query
print("\nLast UPDATE query:")
print(connection.queries[-2]['sql'])

# Verify the result
assert obj.c8 == 'test_name', f"Expected 'test_name', got '{obj.c8}'"
print("\n✅ Test passed! F expression works correctly with bulk_update now.")
