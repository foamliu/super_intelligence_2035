import sys
import os
from pylint import modify_sys_path

cwd = os.getcwd()

# Test that only first entry is popped if it matches
sys.path = [cwd, "/test1", "/test2"]
print(f"Before: {sys.path}")
modify_sys_path()
print(f"After: {sys.path}")
print(f"First entry removed: {sys.path[0] == '/test1'}")
print()

# Test that first entry is not popped if it doesn't match
sys.path = ["/custom/path", "/test1", "/test2"]
print(f"Before: {sys.path}")
modify_sys_path()
print(f"After: {sys.path}")
print(f"First entry preserved: {sys.path[0] == '/custom/path'}")
