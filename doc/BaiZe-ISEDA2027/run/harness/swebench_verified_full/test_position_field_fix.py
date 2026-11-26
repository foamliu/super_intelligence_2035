#!/usr/bin/env python
import sys
import os
import django
from django.conf import settings
from django.db import models
from django.contrib import admin
from django.core import checks

# Configure Django settings
settings.configure(
    DEBUG=True,
    SECRET_KEY='test-secret-key',
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'django.contrib.admin',
    ],
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
)

django.setup()

# Implement a PositionField-like descriptor that raises when accessed on the model class
class PositionFieldDescriptor:
    def __get__(self, instance, owner):
        if instance is None:
            # This is what causes hasattr to return False when called on the model class
            raise AttributeError("PositionField is only accessible on instances")
        return instance.__dict__.get('order', 0)
    
    def __set__(self, instance, value):
        instance.__dict__['order'] = value

class PositionField(models.Field):
    def contribute_to_class(self, cls, name):
        super().contribute_to_class(cls, name)
        setattr(cls, name, PositionFieldDescriptor())

# Create our test model
class Thing(models.Model):
    number = models.IntegerField(default=0)
    order = PositionField()
    
    class Meta:
        app_label = 'test'

# Register the admin
@admin.register(Thing)
class ThingAdmin(admin.ModelAdmin):
    list_display = ['number', 'order']

# Run the checks
print("Running admin checks...")
errors = checks.run_checks()

e108_errors = [e for e in errors if e.id == 'admin.E108']
e109_errors = [e for e in errors if e.id == 'admin.E109']

print(f"Found {len(e108_errors)} E108 errors:")
for e in e108_errors:
    print(f"  - {e.msg}")

print(f"\nFound {len(e109_errors)} E109 errors:")
for e in e109_errors:
    print(f"  - {e.msg}")

if len(e108_errors) == 0:
    print("\n✅ SUCCESS: No E108 error raised for PositionField in list_display!")
    # Also verify that invalid fields still correctly raise E108
    print("\nTesting invalid field to make sure E108 still works...")
    ThingAdmin.list_display = ['number', 'order', 'non_existent_field']
    errors = checks.run_checks()
    e108_errors = [e for e in errors if e.id == 'admin.E108']
    if len(e108_errors) == 1 and 'non_existent_field' in e108_errors[0].msg:
        print("✅ SUCCESS: Invalid field still correctly raises E108!")
        sys.exit(0)
    else:
        print("❌ FAIL: Invalid field didn't raise expected E108 error!")
        sys.exit(1)
else:
    print("\n❌ FAIL: E108 error raised for PositionField!")
    sys.exit(1)
