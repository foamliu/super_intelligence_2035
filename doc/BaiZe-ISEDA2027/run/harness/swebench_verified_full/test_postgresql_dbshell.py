#!/usr/bin/env python3
"""Test script to verify PostgreSQL dbshell SSL parameter support"""

import os
import sys
from unittest.mock import patch, MagicMock

# Add django to path
sys.path.insert(0, '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/django')

from django.db.backends.postgresql.client import DatabaseClient


def test_ssl_params():
    """Test that SSL parameters are correctly passed as environment variables"""
    conn_params = {
        'database': 'testdb',
        'user': 'testuser',
        'password': 'testpass',
        'host': 'postgres',
        'port': '5432',
        'OPTIONS': {
            'sslmode': 'verify-ca',
            'sslrootcert': 'ca.crt',
            'sslcert': 'client_cert_chain.crt',
            'sslkey': 'client_key.key'
        }
    }

    expected_env = {
        'PGPASSWORD': 'testpass',
        'PGSSLMODE': 'verify-ca',
        'PGSSLROOTCERT': 'ca.crt',
        'PGSSLCERT': 'client_cert_chain.crt',
        'PGSSLKEY': 'client_key.key'
    }

    with patch('subprocess.run') as mock_run, patch('os.environ.copy', return_value={}):
        mock_run.return_value = MagicMock(returncode=0)
        DatabaseClient.runshell_db(conn_params)
        
        # Check that subprocess.run was called with the correct env
        call_args = mock_run.call_args
        actual_env = call_args[1]['env']
        
        print("Testing SSL parameters...")
        all_ok = True
        for key, expected_value in expected_env.items():
            actual_value = actual_env.get(key)
            if actual_value == expected_value:
                print(f"✓ {key}: {actual_value} (correct)")
            else:
                print(f"✗ {key}: expected {expected_value}, got {actual_value}")
                all_ok = False
        
        # Check the command line args
        expected_args = ['psql', '-U', 'testuser', '-h', 'postgres', '-p', '5432', 'testdb']
        actual_args = call_args[0][0]
        if actual_args == expected_args:
            print(f"\n✓ Command line args: {' '.join(actual_args)} (correct)")
        else:
            print(f"\n✗ Command line args mismatch:")
            print(f"  Expected: {' '.join(expected_args)}")
            print(f"  Got: {' '.join(actual_args)}")
            all_ok = False
        
        return all_ok


def test_no_ssl_params():
    """Test that no SSL environment variables are set when not configured"""
    conn_params = {
        'database': 'testdb',
        'user': 'testuser',
        'password': 'testpass',
        'OPTIONS': {}
    }

    with patch('subprocess.run') as mock_run, patch('os.environ.copy', return_value={}):
        mock_run.return_value = MagicMock(returncode=0)
        DatabaseClient.runshell_db(conn_params)
        
        call_args = mock_run.call_args
        actual_env = call_args[1]['env']
        
        print("\n\nTesting without SSL parameters...")
        ssl_env_vars = ['PGSSLMODE', 'PGSSLROOTCERT', 'PGSSLCERT', 'PGSSLKEY']
        all_ok = True
        for var in ssl_env_vars:
            if var not in actual_env:
                print(f"✓ {var} not present (correct)")
            else:
                print(f"✗ {var} present when it shouldn't be: {actual_env[var]}")
                all_ok = False
        
        # PGPASSWORD should still be present
        if actual_env.get('PGPASSWORD') == 'testpass':
            print("✓ PGPASSWORD still present (correct)")
        else:
            print("✗ PGPASSWORD missing or incorrect")
            all_ok = False
        
        return all_ok


if __name__ == '__main__':
    print("Testing PostgreSQL dbshell SSL parameter support\n")
    
    test1_ok = test_ssl_params()
    test2_ok = test_no_ssl_params()
    
    if test1_ok and test2_ok:
        print("\n✅ All tests passed! SSL parameters are correctly handled.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
