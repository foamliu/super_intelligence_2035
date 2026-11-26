#!/usr/bin/env python
"""Test that squashed migrations are marked as unapplied when unapplied"""

import os
import tempfile
import shutil
from django.conf import settings
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.recorder import MigrationRecorder

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
        'testapp',
    ],
    SECRET_KEY='test-secret-key',
)

import django
django.setup()

# Create a temporary directory for our test app
temp_dir = tempfile.mkdtemp()
testapp_dir = os.path.join(temp_dir, 'testapp')
os.makedirs(testapp_dir)

# Create __init__.py
with open(os.path.join(testapp_dir, '__init__.py'), 'w') as f:
    f.write('')

# Create migrations directory
migrations_dir = os.path.join(testapp_dir, 'migrations')
os.makedirs(migrations_dir)
with open(os.path.join(migrations_dir, '__init__.py'), 'w') as f:
    f.write('')

# Create model file
with open(os.path.join(testapp_dir, 'models.py'), 'w') as f:
    f.write("""
from django.db import models

class TestModel(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField(default=0)
    email = models.EmailField(default='')
""")

# Add temp dir to path
import sys
sys.path.insert(0, temp_dir)

# Create initial migration 0001
with open(os.path.join(migrations_dir, '0001_initial.py'), 'w') as f:
    f.write("""
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='TestModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
    ]
""")

# Create migration 0002_add_age
with open(os.path.join(migrations_dir, '0002_add_age.py'), 'w') as f:
    f.write("""
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('testapp', '0001_initial'),
    ]
    operations = [
        migrations.AddField(
            model_name='testmodel',
            name='age',
            field=models.IntegerField(default=0),
        ),
    ]
""")

# Create migration 0003_add_email
with open(os.path.join(migrations_dir, '0003_add_email.py'), 'w') as f:
    f.write("""
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('testapp', '0002_add_age'),
    ]
    operations = [
        migrations.AddField(
            model_name='testmodel',
            name='email',
            field=models.EmailField(default=''),
        ),
    ]
""")

# Create squashed migration 0001_squashed_0003
with open(os.path.join(migrations_dir, '0001_squashed_0003.py'), 'w') as f:
    f.write("""
from django.db import migrations, models

class Migration(migrations.Migration):
    replaces = [
        ('testapp', '0001_initial'),
        ('testapp', '0002_add_age'),
        ('testapp', '0003_add_email'),
    ]
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='TestModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('age', models.IntegerField(default=0)),
                ('email', models.EmailField(default='')),
            ],
        ),
    ]
""")

# Run migrations
executor = MigrationExecutor(connection)
executor.migrate([('testapp', '0001_squashed_0003')])

# Check that all migrations are applied
recorder = MigrationRecorder(connection)
applied = recorder.applied_migrations()
print("Applied after migrate:", applied)

# Verify both replaced and squashed are applied
assert ('testapp', '0001_initial') in applied
assert ('testapp', '0002_add_age') in applied
assert ('testapp', '0003_add_email') in applied
assert ('testapp', '0001_squashed_0003') in applied
print("✓ All migrations (replaced + squashed) are correctly applied")

# Now unapply all migrations
executor = MigrationExecutor(connection)
executor.migrate([('testapp', None)])

# Check applied migrations now
applied = recorder.applied_migrations()
print("Applied after unapply:", applied)

# Verify all are unapplied
assert ('testapp', '0001_initial') not in applied
assert ('testapp', '0002_add_age') not in applied
assert ('testapp', '0003_add_email') not in applied
assert ('testapp', '0001_squashed_0003') not in applied, "Squashed migration should be marked as unapplied!"
print("✓ All migrations (replaced + squashed) are correctly unapplied")

# Clean up
shutil.rmtree(temp_dir)
print("\n✅ Test passed! Squashed migration is correctly marked as unapplied when unapplied.")
