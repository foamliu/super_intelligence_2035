import sys
import os

# Import modify_sys_path first before modifying sys.path
from pylint import modify_sys_path

cwd = os.getcwd()

# Test normal case: first entry is empty string (default when running python)
print("Test case 1: first entry is ''")
original_path = sys.path[:]
sys.path = ["", "/other/path", "/another/path"] + original_path
print(f"Before: sys.path[0] = {sys.path[0]}")

modify_sys_path()

print(f"After: sys.path[0] = {sys.path[0]}")
print(f"Empty string removed: {'' not in sys.path}")
print()

# Test case 2: first entry is "."
print("Test case 2: first entry is '.'")
sys.path = [".", "/other/path", "/another/path"] + original_path
print(f"Before: sys.path[0] = {sys.path[0]}")
modify_sys_path()
print(f"After: sys.path[0] = {sys.path[0]}")
print(f"'.' removed: {'.' not in sys.path}")
print()

# Test case 3: first entry is cwd
print("Test case 3: first entry is cwd")
sys.path = [cwd, "/other/path", "/another/path"] + original_path
print(f"Before: sys.path[0] = {sys.path[0]}")
modify_sys_path()
print(f"After: sys.path[0] = {sys.path[0]}")
print(f"cwd removed: {cwd not in sys.path}")
print()

# Test case 4: first entry is something else
print("Test case 4: first entry is custom path")
custom_path = "/my/custom/path"
sys.path = [custom_path, "/other/path", "/another/path"] + original_path
print(f"Before: sys.path[0] = {sys.path[0]}")
modify_sys_path()
print(f"After: sys.path[0] = {sys.path[0]}")
print(f"Custom path preserved: {custom_path in sys.path}")
print(f"First entry still custom: {sys.path[0] == custom_path}")

# Restore original path
sys.path = original_path
