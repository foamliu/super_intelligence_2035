import inspect
import django
from django.db import models
django.setup()

class Person(models.Model):
    name = models.CharField(max_length=100)
    class Meta:
        app_label = 'testapp'

print("Django version:", django.__version__)
print("Signature of bulk_create:", inspect.signature(Person.objects.bulk_create))
print("Expected: (objs, batch_size=None, ignore_conflicts=False)")
print("Actual:", inspect.signature(Person.objects.bulk_create))
