import os
import sys
import django
from django.conf import settings
from django.db import models
from django.db.migrations import Migrations
from django.db.migrations.executor import MigrationExecutor
from django.db import connections

# Configure Django settings
settings.configure(
    DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'test_db_collation',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '3306',
            'OPTIONS': {
                'charset': 'utf8mb4',
            },
        }
    },
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'test_app',
    ],
    USE_TZ=True,
)

django.setup()

# Create test models
class Account(models.Model):
    id = models.CharField(primary_key=True, db_collation='utf8_bin', max_length=22)
    name = models.CharField(max_length=100)
    
    class Meta:
        app_label = 'test_app'

class Address(models.Model):
    id = models.CharField(primary_key=True, db_collation='utf8_bin', max_length=22)
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    street = models.CharField(max_length=100)
    
    class Meta:
        app_label = 'test_app'

class Profile(models.Model):
    id = models.CharField(primary_key=True, db_collation='utf8_bin', max_length=22)
    account = models.ForeignKey(Account, null=True, blank=True, on_delete=models.CASCADE)
    bio = models.TextField()
    
    class Meta:
        app_label = 'test_app'

# Test the SQL generation
from django.db.backends.mysql.schema import DatabaseSchemaEditor
from django.db import connection

with connection.schema_editor() as editor:
    # Test CREATE TABLE SQL for Account
    sql, params = editor.column_sql(Account, Account._meta.get_field('id'))
    print("Account.id column SQL:", sql)
    assert 'COLLATE `utf8_bin`' in sql, "Account.id should have utf8_bin collation"
    
    # Test CREATE TABLE SQL for Address.account
    account_field = Address._meta.get_field('account')
    sql, params = editor.column_sql(Address, account_field)
    print("Address.account column SQL:", sql)
    assert 'COLLATE `utf8_bin`' in sql, "Address.account should have utf8_bin collation inherited from Account.id"
    
    # Test ALTER TABLE SQL for changing collation
    # Simulate changing Account.id collation to utf8mb4_bin
    new_field = models.CharField(primary_key=True, db_collation='utf8mb4_bin', max_length=22)
    new_field.set_attributes_from_name('id')
    new_field.model = Account
    
    old_field = Account._meta.get_field('id')
    alter_sql, _ = editor._alter_column_type_sql(Account, old_field, new_field, new_field.db_type(connection))
    print("ALTER COLUMN SQL for Account.id:", alter_sql[0])
    assert 'COLLATE `utf8mb4_bin`' in alter_sql[0], "ALTER COLUMN should include new collation"
    
    # Test foreign key alter SQL
    old_fk_field = Address._meta.get_field('account')
    # The new foreign key field should automatically inherit the new collation from Account.id
    new_fk_field = models.OneToOneField(Account, on_delete=models.CASCADE)
    new_fk_field.set_attributes_from_name('account')
    new_fk_field.model = Address
    # Resolve related field
    new_fk_field.remote_field.model = Account
    new_fk_field.remote_field.field_name = 'id'
    
    print("Foreign key db_collation:", new_fk_field.db_collation)
    assert new_fk_field.db_collation == 'utf8mb4_bin', "Foreign key should inherit collation from target field"
    
    alter_fk_sql, _ = editor._alter_column_type_sql(Address, old_fk_field, new_fk_field, new_fk_field.db_type(connection))
    print("ALTER COLUMN SQL for Address.account:", alter_fk_sql[0])
    assert 'COLLATE `utf8mb4_bin`' in alter_fk_sql[0], "ALTER COLUMN for foreign key should include inherited collation"

print("\nAll tests passed! The db_collation is correctly propagated to foreign keys.")
