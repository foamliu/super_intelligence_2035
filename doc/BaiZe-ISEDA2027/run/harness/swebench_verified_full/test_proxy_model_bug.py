import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django'))
import django
from django.conf import settings
from django.db import models, connection
from django.core.management import execute_from_command_line

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
    ROOT_URLCONF='',
)

django.setup()

# Define the models as per the user's example
class CustomModel(models.Model):
    name = models.CharField(max_length=16)
    class Meta:
        app_label = 'test'

class ProxyCustomModel(CustomModel):
    class Meta:
        proxy = True
        app_label = 'test'

class AnotherModel(models.Model):
    custom = models.ForeignKey(
        ProxyCustomModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    class Meta:
        app_label = 'test'

# Create tables
with connection.schema_editor() as editor:
    editor.create_model(CustomModel)
    editor.create_model(AnotherModel)

# Test data
custom = ProxyCustomModel.objects.create(name="Test")
AnotherModel.objects.create(custom=custom)

# Test the problematic query
try:
    objs = list(AnotherModel.objects.select_related("custom").only("custom__name").all())
    print("SUCCESS: Query executed without error!")
    print(f"Retrieved {len(objs)} objects")
    print(f"First object custom name: {objs[0].custom.name}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
