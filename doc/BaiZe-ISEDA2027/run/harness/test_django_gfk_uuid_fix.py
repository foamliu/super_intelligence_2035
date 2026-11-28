import uuid
import os
import sys
import django
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
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
    ],
)

django.setup()

# Create test models
class Foo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'test'

class Bar(models.Model):
    foo_content_type = models.ForeignKey(
        ContentType, related_name='actor',
        on_delete=models.CASCADE, db_index=True
    )
    foo_object_id = models.CharField(max_length=255, db_index=True)
    foo = GenericForeignKey('foo_content_type', 'foo_object_id')
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'test'

# Create tables
from django.db import connection
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(Foo)
    schema_editor.create_model(Bar)

# Test the fix
print("Creating test data...")
foo1 = Foo.objects.create(name="Foo 1")
foo2 = Foo.objects.create(name="Foo 2")

Bar.objects.create(foo=foo1, name="Bar 1")
Bar.objects.create(foo=foo2, name="Bar 2")
Bar.objects.create(name="Bar 3 (no foo)")

print("\nTesting prefetch_related('foo')...")
bars = Bar.objects.all().prefetch_related('foo')

for bar in bars:
    foo_val = bar.foo
    print(f"Bar {bar.name}: foo = {foo_val!r} (object_id: {bar.foo_object_id!r}, content_type: {bar.foo_content_type!r})")

# Verify all foos are correctly retrieved
count_with_foo = sum(1 for bar in bars if bar.foo is not None)
print(f"\nTotal bars with foo: {count_with_foo} (expected 2)")
print(f"Test {'PASSED' if count_with_foo == 2 else 'FAILED'}")

if count_with_foo == 2:
    print("\n✅ Fix works! prefetch_related now correctly loads GenericForeignKey relationships to models with UUID primary keys.")
else:
    print("\n❌ Fix failed! Some foos are not loaded correctly.")
    sys.exit(1)
