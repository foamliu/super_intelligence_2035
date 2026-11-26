"""
Test case for the Django Query.change_aliases AssertionError bug.
This reproduces the exact scenario described by the user.
"""

import sys
import os
import django
from django.conf import settings
from django.db import models
from django.db.models import Q

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
        'bug.app',
    ]
)

django.setup()

# Define the models as per the user's report
class Qux(models.Model):
    bazes = models.ManyToManyField("app.Baz", related_name="quxes")
    
    class Meta:
        app_label = 'app'

class Baz(models.Model):
    class Meta:
        app_label = 'app'

class Foo(models.Model):
    qux = models.ForeignKey("app.Qux", on_delete=models.CASCADE, related_name="foos")
    
    class Meta:
        app_label = 'app'

class Bar(models.Model):
    foo = models.ForeignKey("app.Foo", on_delete=models.CASCADE, related_name="bars")
    another_foo = models.ForeignKey("app.Foo", on_delete=models.CASCADE, related_name="other_bars")
    baz = models.ForeignKey("app.Baz", on_delete=models.CASCADE, related_name="bars")
    
    class Meta:
        app_label = 'app'

# Create tables
from django.db import connection
with connection.schema_editor() as schema_editor:
    for model in [Qux, Baz, Foo, Bar]:
        schema_editor.create_model(model)

# Test the bug
print("Testing the bug scenario...")
qux = Qux.objects.create()
baz = Baz.objects.create()
qux.bazes.add(baz)
foo = Foo.objects.create(qux=qux)
bar = Bar.objects.create(foo=foo, another_foo=foo, baz=baz)

qs1 = qux.foos.all()
print(f"qs1 query: {qs1.query}")
print(f"qs1 aliases: {list(qs1.query.alias_map.keys())}")

qs2 = Foo.objects.filter(
    Q(bars__baz__in=qux.bazes.all()) | Q(other_bars__baz__in=qux.bazes.all())
)
print(f"\nqs2 query: {qs2.query}")
print(f"qs2 aliases: {list(qs2.query.alias_map.keys())}")

# This should work fine
print("\nTesting qs2 | qs1...")
try:
    qs_combined1 = qs2 | qs1
    print("✓ qs2 | qs1 works fine")
    print(f"Combined query count: {qs_combined1.count()}")
except Exception as e:
    print(f"✗ qs2 | qs1 failed: {type(e).__name__}: {e}")

# This used to raise AssertionError before the fix
print("\nTesting qs1 | qs2...")
try:
    qs_combined2 = qs1 | qs2
    print("✓ qs1 | qs2 works fine (bug fixed!)")
    print(f"Combined query count: {qs_combined2.count()}")
    print(f"Both combined queries return the same results: {list(qs_combined1) == list(qs_combined2)}")
except AssertionError as e:
    print(f"✗ qs1 | qs2 failed with AssertionError (bug present): {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"✗ qs1 | qs2 failed with unexpected error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
