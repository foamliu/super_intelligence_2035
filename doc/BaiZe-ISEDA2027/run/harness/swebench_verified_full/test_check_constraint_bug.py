"""Test case to reproduce the CheckConstraint OR bug"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django'))
import django
from django.conf import settings
from django.db import models
from django.db.models import Q, CheckConstraint
from django.db.backends.sqlite3.schema import DatabaseSchemaEditor
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

# Define the test model
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

# Test the constraint SQL generation
with connection.schema_editor() as editor:
    # Let's see what happens when we create the model
    sql = editor.sql_create_table % {
        "table": editor.quote_name(TestConstraint._meta.db_table),
        "definition": ", ".join(
            constraint for constraint in (
                *(
                    f"{editor.quote_name(field.column)} {editor.column_sql(TestConstraint, field)[0]}"
                    for field in TestConstraint._meta.local_fields
                ),
                *(
                    constraint.constraint_sql(TestConstraint, editor)
                    for constraint in TestConstraint._meta.constraints
                )
            ) if constraint
        ),
    }
    print("Normal create table SQL:")
    print(sql)
    print("\n")
    
    # Now simulate what happens in _remake_table
    # Create a new model with db_table = 'new__app_testconstraint'
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
    
    # Get the constraint SQL for the new model
    new_constraint_sql = NewTestConstraint._meta.constraints[0].constraint_sql(NewTestConstraint, editor)
    print("Constraint SQL for new__ table:")
    print(new_constraint_sql)
    print("\n")
    
    # Let's see what _get_unqualified_sql returns
    constraint = NewTestConstraint._meta.constraints[0]
    check_sql = constraint._get_check_sql(NewTestConstraint, editor)
    print("_get_check_sql output:")
    print(check_sql)
