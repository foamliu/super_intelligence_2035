import os
import sys
import datetime
from django.conf import settings
from django.db import models
from django import forms

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

import django
django.setup()

# Define the model
def default_mode():
    return 'di'

def default_category():
    return 1

class PublicationDefaults(models.Model):
    MODE_CHOICES = (('di', 'direct'), ('de', 'delayed'))
    CATEGORY_CHOICES = ((1, 'Games'), (2, 'Comics'), (3, 'Novel'))
    title = models.CharField(max_length=30)
    date_published = models.DateField(default=datetime.date.today)
    mode = models.CharField(max_length=2, choices=MODE_CHOICES, default=default_mode)
    category = models.IntegerField(choices=CATEGORY_CHOICES, default=default_category)
    active = models.BooleanField(default=True)

    class Meta:
        app_label = 'test'

# Create tables
from django.db import connection
with connection.schema_editor() as editor:
    editor.create_model(PublicationDefaults)

# Test case 1: Default behavior (no clean method override)
print("Test 1: Default behavior (no clean method)")
class PubForm1(forms.ModelForm):
    mode = forms.CharField(max_length=255, required=False)
    category = forms.IntegerField(required=False)

    class Meta:
        model = PublicationDefaults
        fields = ('mode', 'category', 'title')

form1 = PubForm1({'title': 'Test 1'})
assert form1.is_valid(), f"Form1 invalid: {form1.errors}"
instance1 = form1.save(commit=False)
print(f"  mode: {instance1.mode} (expected 'di')")
print(f"  category: {instance1.category} (expected 1)")
assert instance1.mode == 'di'
assert instance1.category == 1
print("  ✓ Passed\n")

# Test case 2: Clean method overrides values not in form data
print("Test 2: Clean method sets values not in form data")
class PubForm2(forms.ModelForm):
    mode = forms.CharField(max_length=255, required=False)
    category = forms.IntegerField(required=False)

    class Meta:
        model = PublicationDefaults
        fields = ('mode', 'category', 'title')

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['mode'] = 'de'
        cleaned_data['category'] = 3
        return cleaned_data

form2 = PubForm2({'title': 'Test 2'})
assert form2.is_valid(), f"Form2 invalid: {form2.errors}"
instance2 = form2.save(commit=False)
print(f"  mode: {instance2.mode} (expected 'de')")
print(f"  category: {instance2.category} (expected 3)")
assert instance2.mode == 'de'
assert instance2.category == 3
print("  ✓ Passed\n")

# Test case 3: Empty string submitted uses empty value, not default
print("Test 3: Empty string submitted")
form3 = PubForm1({'title': 'Test 3', 'mode': ''})
assert form3.is_valid(), f"Form3 invalid: {form3.errors}"
instance3 = form3.save(commit=False)
print(f"  mode: '{instance3.mode}' (expected empty string)")
assert instance3.mode == ''
print("  ✓ Passed\n")

# Test case 4: Checkbox field (active) works correctly
print("Test 4: Checkbox field not submitted")
class PubForm4(forms.ModelForm):
    class Meta:
        model = PublicationDefaults
        fields = ('active', 'title')

form4 = PubForm4({'title': 'Test 4'})
assert form4.is_valid(), f"Form4 invalid: {form4.errors}"
instance4 = form4.save(commit=False)
print(f"  active: {instance4.active} (expected False)")
assert instance4.active is False
print("  ✓ Passed\n")

print("All tests passed! ✅")
