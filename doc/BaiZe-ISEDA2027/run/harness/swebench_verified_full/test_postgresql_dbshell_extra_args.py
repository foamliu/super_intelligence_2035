#!/usr/bin/env python3
"""Test script to verify PostgreSQL dbshell extra parameters are passed correctly before dbname"""

import sys
from unittest.mock import patch, MagicMock

# Add django to path
sys.path.insert(0, '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/django')

from django.db.backends.postgresql.client import DatabaseClient
from django.core.management.commands.dbshell import Command
from django.db import connections


def test_postgresql_extra_args():
    """Test that extra arguments are passed before dbname"""
    conn_params = {
        'database': 'testdb',
        'user': 'testuser',
        'host': 'postgres',
        'port': '5432',
    }

    extra_args = ['-c', 'select * from some_table;']

    with patch('subprocess.run') as mock_run, patch('os.environ.copy', return_value={}):
        mock_run.return_value = MagicMock(returncode=0)
        DatabaseClient.runshell_db(conn_params, extra_args)
        
        call_args = mock_run.call_args
        actual_args = call_args[0][0]
        
        # Check that args are in the correct order: psql options + extra args + dbname
        expected_args = ['psql', '-U', 'testuser', '-h', 'postgres', '-p', '5432', '-c', 'select * from some_table;', 'testdb']
        
        print("Testing PostgreSQL extra args order...")
        if actual_args == expected_args:
            print(f"✓ Command line args: {' '.join(actual_args)} (correct)")
            print("✓ Extra args are placed before dbname as expected")
            return True
        else:
            print(f"✗ Command line args mismatch:")
            print(f"  Expected: {' '.join(expected_args)}")
            print(f"  Got:      {' '.join(actual_args)}")
            return False


def test_dbshell_command_passes_args():
    """Test that dbshell command correctly passes extra arguments"""
    # Mock the connection
    mock_client = MagicMock()
    mock_connection = MagicMock()
    mock_connection.client = mock_client
    mock_connection.client.executable_name = 'psql'
    
    # connections is a dict-like object, not a function
    with patch('django.core.management.commands.dbshell.connections', {'default': mock_connection}):
        cmd = Command()
        # Simulate passing extra args: ./manage.py dbshell -- -c "select * from test"
        cmd.handle('-c', 'select * from test', database='default')
        
        # Check that runshell was called with the extra args
        if mock_client.runshell.called:
            call_args = mock_client.runshell.call_args
            passed_args = call_args[0][0]
            if passed_args == ('-c', 'select * from test'):
                print("\n✓ Dbshell command correctly passes extra arguments to client.runshell()")
                return True
            else:
                print(f"\n✗ Dbshell command passed wrong args: {passed_args}")
                return False
        else:
            print("\n✗ Dbshell command did not call runshell()")
            return False


if __name__ == '__main__':
    print("Testing PostgreSQL dbshell extra parameters fix\n")
    
    test1_ok = test_postgresql_extra_args()
    test2_ok = test_dbshell_command_passes_args()
    
    if test1_ok and test2_ok:
        print("\n✅ All tests passed! Extra parameters are now correctly passed before dbname.")
        print("\nThe issue is fixed: running ./manage.py dbshell -- -c \"select * from some_table;\" will work correctly now.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
