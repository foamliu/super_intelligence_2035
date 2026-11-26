#!/usr/bin/env python
import sys
import os
sys.path.insert(0, 'django')

import django
from django.conf import settings
from django.db import models
from django.contrib.admin.checks import ModelAdminChecks
from django.contrib.admin.options import ModelAdmin
from django.core.exceptions import FieldDoesNotExist

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

# Create admin instance
class ThingAdmin(ModelAdmin):
    list_display = ['number', 'order']

admin_instance = ThingAdmin(Thing, None)
checker = ModelAdminChecks()

print("Testing PositionField 'order' in list_display:")
errors = checker._check_list_display_item(admin_instance, 'order', 'list_display[1]')
print(f"Errors: {errors}")
if len(errors) == 0:
    print("✅ PASS: No error for valid PositionField")
else:
    print(f"❌ FAIL: Got error {errors[0].id}: {errors[0].msg}")
    sys.exit(1)

print("\nTesting non-existent field 'non_existent' in list_display:")
errors = checker._check_list_display_item(admin_instance, 'non_existent', 'list_display[2]')
print(f"Errors: {errors}")
if len(errors) == 1 and errors[0].id == 'admin.E108':
    print("✅ PASS: Correctly raised E108 for non-existent field")
else:
    print(f"❌ FAIL: Expected E108, got {errors}")
    sys.exit(1)

print("\nTesting ManyToManyField in list_display:")
class ManyModel(models.Model):
    items = models.ManyToManyField('self')
    
    class Meta:
        app_label = 'test'

class ManyAdmin(ModelAdmin):
    list_display = ['items']

many_admin = ManyAdmin(ManyModel, None)
errors = checker._check_list_display_item(many_admin, 'items', 'list_display[0]')
print(f"Errors: {errors}")
if len(errors) == 1 and errors[0].id == 'admin.E109':
    print("✅ PASS: Correctly raised E109 for ManyToManyField")
else:
    print(f"❌ FAIL: Expected E109, got {errors}")
    sys.exit(1)

print("\n✅ All tests passed!")
