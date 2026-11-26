import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django'))
import django
from django.conf import settings
from uuid import uuid4
from django.db import models

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
    ]
)

django.setup()

# Define the model
class Sample(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(blank=True, max_length=100)

    class Meta:
        app_label = 'test'

# Create tables
from django.db import connection
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(Sample)

# Test the issue
print("Testing UUID pk save issue...")
s0 = Sample.objects.create()
print(f"Created s0 with pk: {s0.pk}")

s1 = Sample(pk=s0.pk, name='Test 1')
print(f"Created s1 with pk: {s1.pk}, _state.adding: {s1._state.adding}")

try:
    s1.save()
    print(f"s1 saved successfully. name: {s1.name}, _state.adding now: {s1._state.adding}")
    
    # Check if there's one or two rows
    count = Sample.objects.count()
    print(f"Total Sample rows: {count}")
    if count == 1:
        print("✅ Correct: Only one row exists, save did an UPDATE")
    else:
        print("❌ Wrong: Multiple rows exist, save did an INSERT instead of UPDATE")
        
except Exception as e:
    print(f"❌ Error saving s1: {e}")
    print("This is the bug: second INSERT fails because pk already exists")
