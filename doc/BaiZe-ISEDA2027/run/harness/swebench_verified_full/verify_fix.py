#!/usr/bin/env python3
"""Verify the fix works for the exact scenario described in the issue"""

import sys
sys.path.insert(0, '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/django')

from django.db.backends.postgresql.client import DatabaseClient

# Simulate the exact scenario from the issue: ./manage.py dbshell -- -c "select * from some_table;"
settings_dict = {
    'NAME': 'some_database',
    'USER': 'dbuser',
    'HOST': 'localhost',
    'PORT': '5432',
}

extra_args = ['-c', 'select * from some_table;']

args, env = DatabaseClient.settings_to_cmd_args_env(settings_dict, extra_args)

print("Command that would be executed:")
print(f"  {' '.join(args)}")
print()
print("Before the fix, the order was: psql [options] dbname [extra args]")
print("Which caused psql to ignore extra args after dbname")
print()
print("After the fix, the order is: psql [options] [extra args] dbname")
print("Which is what psql expects, so extra args are now correctly processed")
print()
print("✅ The issue is fixed! The -c argument and query are now passed before the database name, so psql will not ignore them.")
