import os
import sys
import django
from django.db import models
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
    ]
)

django.setup()

# Define the custom field with from_db_value
class MyIntWrapper(int):
    pass

class MyAutoField(models.BigAutoField):
    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        return MyIntWrapper(value)
    
    def get_prep_value(self, value):
        if value is None:
            return None
        return int(value)

# Define the model
class AutoModel(models.Model):
    id = MyAutoField(primary_key=True)
    
    class Meta:
        app_label = 'test'

# Create tables
from django.db import connection
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(AutoModel)

print("Testing create()...")
am2 = AutoModel.objects.create()
print(f"am2.id type: {type(am2.id)}, value: {am2.id}")
assert isinstance(am2.id, MyIntWrapper), f"Expected MyIntWrapper, got {type(am2.id)}"
print("✓ create() works correctly")

print("\nTesting bulk_create()...")
ams = [AutoModel(), AutoModel()]
AutoModel.objects.bulk_create(ams)
for i, am in enumerate(ams):
    print(f"ams[{i}].id type: {type(am.id)}, value: {am.id}")
    assert isinstance(am.id, MyIntWrapper), f"Expected MyIntWrapper for ams[{i}], got {type(am.id)}"
print("✓ bulk_create() works correctly")

print("\nTesting get()...")
am = AutoModel.objects.first()
print(f"am.id type: {type(am.id)}, value: {am.id}")
assert isinstance(am.id, MyIntWrapper), f"Expected MyIntWrapper, got {type(am.id)}"
print("✓ get() works correctly (as expected)")

print("\n✅ All tests passed!")
