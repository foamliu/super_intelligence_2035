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
    ],
)

django.setup()

# Create test model
class Foo(models.Model):
    uuid = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['name']

# Create tables
from django.db import connection
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(Foo)

# Test the fix
print("Testing QuerySet.ordered property fix:")
print("=" * 50)

qs = Foo.objects.all()
print(f"qs = Foo.objects.all()")
print(f"qs.ordered: {qs.ordered} (expected: True)")
print(f"SQL: {qs.query}")
print()

from django.db.models import Count
qs2 = Foo.objects.annotate(Count("pk")).all()
print(f"qs2 = Foo.objects.annotate(Count('pk')).all()")
print(f"qs2.ordered: {qs2.ordered} (expected: False)")
print(f"SQL: {qs2.query}")
print()

qs3 = Foo.objects.annotate(Count("pk")).order_by('name').all()
print(f"qs3 = Foo.objects.annotate(Count('pk')).order_by('name').all()")
print(f"qs3.ordered: {qs3.ordered} (expected: True)")
print(f"SQL: {qs3.query}")
print()

print("=" * 50)
print("Test completed!")
