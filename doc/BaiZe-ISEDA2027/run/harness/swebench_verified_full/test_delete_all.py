
import os
import sys
import django
from django.conf import settings
from django.db import models
from django.db import connection

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

# Define a simple model
class TestModel(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        app_label = 'test'

# Create tables
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(TestModel)

# Insert some data
for i in range(10):
    TestModel.objects.create(name=f"Test {i}")

# Test delete all
from django.db import connection
with connection.queries_log() as queries:
    TestModel.objects.all().delete()
    print("Number of queries:", len(queries))
    for q in queries:
        print("SQL:", q['sql'])
