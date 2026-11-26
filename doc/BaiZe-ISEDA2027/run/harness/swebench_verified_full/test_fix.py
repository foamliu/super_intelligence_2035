import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django'))
import django
from django.conf import settings
from uuid import uuid4
from django.db import models

# Configure Django
settings.configure(
    DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    INSTALLED_APPS=[],
)
django.setup()

# Test 1: UUIDField with default (the bug case)
class Sample(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(blank=True, max_length=100)
    
    class Meta:
        app_label = 'test'

# Test 2: AutoField (default)
class AutoSample(models.Model):
    name = models.CharField(blank=True, max_length=100)
    
    class Meta:
        app_label = 'test'

# Create tables
from django.db import connection
with connection.schema_editor() as editor:
    editor.create_model(Sample)
    editor.create_model(AutoSample)

print("=== Test 1: UUIDField with default ===")
s0 = Sample.objects.create(name="Original")
print(f"Created s0: pk={s0.pk}, name={s0.name}")

# Create new instance with existing pk
s1 = Sample(pk=s0.pk, name="Updated")
print(f"Created s1: pk={s1.pk}, name={s1.name}, _state.adding={s1._state.adding}")

try:
    s1.save()
    print("s1.save() succeeded")
    
    # Check the result
    s2 = Sample.objects.get(pk=s0.pk)
    print(f"After save, name in DB: {s2.name}")
    print(f"Total rows: {Sample.objects.count()}")
    
    if s2.name == "Updated" and Sample.objects.count() == 1:
        print("✅ PASS: Correctly did UPDATE instead of INSERT")
    else:
        print("❌ FAIL: Did INSERT instead of UPDATE")
        
except Exception as e:
    print(f"❌ FAIL: Error saving s1: {e}")

print("\n=== Test 2: AutoField (default behavior) ===")
a0 = AutoSample.objects.create(name="Original")
print(f"Created a0: pk={a0.pk}, name={a0.name}")

# Create new instance with existing pk (should do INSERT, fail with unique constraint)
a1 = AutoSample(pk=a0.pk, name="Updated")
print(f"Created a1: pk={a1.pk}, name={a1.name}, _state.adding={a1._state.adding}")

try:
    a1.save()
    print("❌ FAIL: Should have raised IntegrityError but succeeded")
except Exception as e:
    print(f"✅ PASS: Correctly raised error (tried to INSERT duplicate pk): {type(e).__name__}")
