import os
import sys
import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django'))
import django
from django.conf import settings
from django.db import models
from django.db.models import F

# Configure Django settings for SQLite test
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

# Define test model
class Experiment(models.Model):
    estimated_time = models.DurationField()
    
    class Meta:
        app_label = 'test'

# Create tables
from django.db import connection
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(Experiment)

# Test the fix
print("Testing SQLite duration expression...")
exp = Experiment.objects.create(estimated_time=datetime.timedelta(hours=2))
result = list(Experiment.objects.annotate(duration=F('estimated_time') + datetime.timedelta(days=1)))
print(f"Success! Result: {result[0].duration}")
print(f"Expected: 1 day, 2:00:00, Got: {result[0].duration}")
assert result[0].duration == datetime.timedelta(days=1, hours=2)
print("SQLite test passed!")

# Now test MySQL if available
# This part requires MySQL server running and credentials set
if '--mysql' in sys.argv:
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DB', 'test'),
        'USER': os.environ.get('MYSQL_USER', 'root'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD', ''),
        'HOST': os.environ.get('MYSQL_HOST', 'localhost'),
        'PORT': os.environ.get('MYSQL_PORT', '3306'),
    }
    # Clear existing tables
    with connection.schema_editor() as schema_editor:
        schema_editor.delete_model(Experiment)
    # Create tables for MySQL
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(Experiment)
    
    print("\nTesting MySQL duration expression...")
    exp = Experiment.objects.create(estimated_time=datetime.timedelta(hours=2))
    result = list(Experiment.objects.annotate(duration=F('estimated_time') + datetime.timedelta(days=1)))
    print(f"Success! Result: {result[0].duration}")
    print(f"Expected: 1 day, 2:00:00, Got: {result[0].duration}")
    assert result[0].duration == datetime.timedelta(days=1, hours=2)
    print("MySQL test passed!")
