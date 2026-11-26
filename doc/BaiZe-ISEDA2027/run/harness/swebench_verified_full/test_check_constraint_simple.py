"""Simple test for the CheckConstraint OR operator fix for SQLite and Oracle."""

import sys

# Add Django to path
sys.path.insert(0, '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/django')

import django
from django.conf import settings
from django.db import models
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
    INSTALLED_APPS=[],
)

django.setup()

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
from django.db import connection

with connection.schema_editor() as editor:
    constraint = TestConstraint._meta.constraints[0]
    sql = constraint.constraint_sql(TestConstraint, editor)
    print(f"\nGenerated constraint SQL: {sql}")
    
    # Check that there are no table-qualified column names
    has_table_qualification = '.' in sql and ('field_1' in sql or 'flag' in sql)
    if has_table_qualification:
        print("\n❌ ERROR: Constraint SQL contains table-qualified column names!")
        print("This would cause the migration to fail when SQLite renames the table.")
    else:
        print("\n✅ SUCCESS: Constraint SQL correctly generated without table qualifications!")
        print("This will work correctly when SQLite renames tables during migrations.")
    
    # Show the expected vs actual
    print("\nExpected format: CHECK ((\"field_1\" IS NOT NULL AND \"flag\" = 1) OR \"flag\" = 0)")
    print(f"Actual:         {sql}")
    
    # Verify the logic is still correct
    expected_logic = ('"field_1" IS NOT NULL' in sql or '`field_1` IS NOT NULL' in sql) and \
                     ('"flag" = 1' in sql or '`flag` = 1' in sql) and \
                     ('"flag" = 0' in sql or '`flag` = 0' in sql) and \
                     'OR' in sql and 'AND' in sql
    
    if expected_logic:
        print("\n✅ Constraint logic is preserved correctly")
    else:
        print("\n❌ ERROR: Constraint logic is not preserved!")

print("\nTest complete.")
