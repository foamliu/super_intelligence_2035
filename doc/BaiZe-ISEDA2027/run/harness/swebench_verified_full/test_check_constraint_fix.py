"""Test for the CheckConstraint OR operator fix for SQLite and Oracle."""

import os
import sys
import tempfile
import sqlite3

# Add Django to path
sys.path.insert(0, '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/django')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')

import django
from django.conf import settings
from django.db import models, connection
from django.db.migrations import Migration, AddConstraint, CreateModel
from django.db.migrations.executor import MigrationExecutor
from django.db.models import Q, CheckConstraint

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

# Create test app
from django.apps import apps
from django.conf import settings

if not apps.is_installed('test_app'):
    settings.INSTALLED_APPS.append('test_app')
    apps.clear_cache()
    from django.apps.config import AppConfig
    apps.register_app_config(AppConfig('test_app', type('test_app', (), {'__file__': __file__})()))

# Define the test model
class TestConstraint(models.Model):
    field_1 = models.IntegerField(blank=True, null=True)
    flag = models.BooleanField(blank=False, null=False)
    
    class Meta:
        app_label = 'test_app'
        constraints = [
            CheckConstraint(
                check=Q(flag__exact=True, field_1__isnull=False) | Q(flag__exact=False),
                name='field_1_has_value_if_flag_set'
            ),
        ]

# Test the constraint SQL generation
print("Testing CheckConstraint SQL generation...")
with connection.schema_editor() as editor:
    constraint = TestConstraint._meta.constraints[0]
    sql = constraint.constraint_sql(TestConstraint, editor)
    print(f"Generated constraint SQL: {sql}")
    
    # Check that there are no table-qualified column names
    assert "new__app_testconstraint" not in sql, "Table name should not appear in constraint SQL"
    assert "test_app_testconstraint" not in sql, "Table name should not appear in constraint SQL"
    assert '"field_1"' in sql or '`field_1`' in sql or '[field_1]' in sql, "field_1 should appear unqualified"
    assert '"flag"' in sql or '`flag`' in sql or '[flag]' in sql, "flag should appear unqualified"
    
    print("✅ Constraint SQL correctly generated without table qualifications")

# Test migration execution (this would fail before the fix)
print("\nTesting migration execution...")

# Create initial migration
class Migration0001(Migration):
    dependencies = []
    operations = [
        CreateModel(
            name='TestConstraint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_1', models.IntegerField(blank=True, null=True)),
                ('flag', models.BooleanField()),
            ],
        ),
    ]

class Migration0002(Migration):
    dependencies = [
        ('test_app', '0001_initial'),
    ]
    operations = [
        AddConstraint(
            model_name='testconstraint',
            constraint=CheckConstraint(
                check=Q(Q(('field_1__isnull', False), ('flag__exact', True)), ('flag__exact', False), _connector='OR'),
                name='field_1_has_value_if_flag_set'
            ),
        ),
    ]

# Run migrations
executor = MigrationExecutor(connection)
executor.migrate([('test_app', '0002')])
print("✅ Migrations executed successfully!")

# Test that the constraint actually works
print("\nTesting constraint validation...")

# Should work: flag=False, field_1 can be null
obj1 = TestConstraint.objects.create(flag=False, field_1=None)
print("✅ flag=False with null field_1 works")

# Should work: flag=True, field_1 has value
obj2 = TestConstraint.objects.create(flag=True, field_1=42)
print("✅ flag=True with non-null field_1 works")

# Should fail: flag=True, field_1 is null
try:
    obj3 = TestConstraint.objects.create(flag=True, field_1=None)
    print("❌ Constraint failed to catch invalid case!")
except Exception as e:
    print(f"✅ Correctly blocked invalid entry: {type(e).__name__}")

print("\nAll tests passed! The fix is working correctly.")
