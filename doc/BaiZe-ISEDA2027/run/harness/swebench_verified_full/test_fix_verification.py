"""Test to verify the CheckConstraint OR fix works correctly"""
import os
import sys
import django
from django.conf import settings
from django.db import models
from django.db.models import Q, CheckConstraint
from django.db.backends.sqlite3.schema import DatabaseSchemaEditor
from django.db import connection

# Configure Django
sys.path.insert(0, '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/django')

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

# Test model from the issue
class TestConstraint(models.Model):
    field_1 = models.IntegerField(blank=True, null=True)
    flag = models.BooleanField(blank=False, null=False)
    
    class Meta:
        app_label = 'app'
        constraints = [
            CheckConstraint(
                check=Q(flag__exact=True, field_1__isnull=False) | Q(flag__exact=False,),
                name='field_1_has_value_if_flag_set'
            ),
        ]

print("Testing CheckConstraint SQL generation for OR condition...")

with connection.schema_editor() as editor:
    # Test the constraint SQL generation
    constraint = TestConstraint._meta.constraints[0]
    sql = constraint.constraint_sql(TestConstraint, editor)
    
    print(f"Generated constraint SQL: {sql}")
    
    # Check that there are no table prefixes in the CHECK clause
    if 'new__app_testconstraint' in sql:
        print("❌ FAILED: Table prefix found in constraint SQL")
    elif 'app_testconstraint' in sql:
        print("❌ FAILED: Table prefix found in constraint SQL")
    else:
        print("✅ SUCCESS: No table prefixes in constraint SQL")
    
    # Verify the SQL is correct
    expected_substring = 'CHECK (("field_1" IS NOT NULL AND "flag" = 1) OR "flag" = 0)'
    if expected_substring in sql:
        print("✅ SUCCESS: Correct SQL generated")
    else:
        print(f"❌ FAILED: Expected substring not found: {expected_substring}")

# Test with the new__ table name scenario (like SQLite _remake_table)
print("\nTesting with new__ table prefix scenario...")
from django.db.models.base import ModelBase
new_meta_contents = {
    'app_label': 'app',
    'db_table': 'new__app_testconstraint',
    'constraints': TestConstraint._meta.constraints,
}
new_meta = type("Meta", (), new_meta_contents)
new_body = {
    'field_1': models.IntegerField(blank=True, null=True),
    'flag': models.BooleanField(blank=False, null=False),
    'Meta': new_meta,
    '__module__': TestConstraint.__module__,
}
NewTestConstraint = ModelBase('NewTestConstraint', TestConstraint.__bases__, new_body)

with connection.schema_editor() as editor:
    constraint = NewTestConstraint._meta.constraints[0]
    sql = constraint.constraint_sql(NewTestConstraint, editor)
    
    print(f"Generated constraint SQL for new__ table: {sql}")
    
    # Check that there are no table prefixes
    if 'new__app_testconstraint' in sql:
        print("❌ FAILED: new__ table prefix found in constraint SQL")
    else:
        print("✅ SUCCESS: No new__ table prefix in constraint SQL")

print("\nFix verified successfully!")
