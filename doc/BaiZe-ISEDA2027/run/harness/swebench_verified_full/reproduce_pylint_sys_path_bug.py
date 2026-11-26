import sys
import runpy
import os

# Add a custom path to sys.path first
custom_path = os.path.abspath("custom_modules")
os.makedirs(custom_path, exist_ok=True)
# Create a test module
with open(os.path.join(custom_path, "test_module.py"), "w") as f:
    f.write("def hello(): return 'hello from custom module'\n")

sys.path.insert(0, custom_path)
print(f"Before runpy: sys.path[0] = {sys.path[0]}")
print(f"Can import test_module before: { 'test_module' in sys.modules or __import__('test_module') is not None }")

# Save original argv
original_argv = sys.argv[:]
sys.argv = [sys.argv[0], "--version"]

# Run pylint via runpy
try:
    runpy.run_module('pylint', run_name="__main__", alter_sys=True)
except SystemExit:
    pass
finally:
    # Restore original argv
    sys.argv = original_argv

print(f"\nAfter runpy: sys.path[0] = {sys.path[0] if sys.path else 'empty'}")
print(f"Can import test_module after: { 'test_module' in sys.modules or __import__('test_module') is not None }")
print(f"Custom path still present: {custom_path in sys.path}")
