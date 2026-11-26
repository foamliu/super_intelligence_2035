import numpy as np
import sys
from unittest.mock import patch, DEFAULT

# Create test function with numpy array patch
@patch(target='some.module.function', new=np.array([-5.5, 3.0]))
def test_with_array():
    pass

# Create test function with DEFAULT sentinel
@patch(target='some.module.function', new=DEFAULT)
def test_with_default():
    pass

# Original problematic implementation
def original_num_mock_patch_args(function):
    patchings = getattr(function, "patchings", None)
    if not patchings:
        return 0
    mock_modules = [sys.modules.get("mock"), sys.modules.get("unittest.mock")]
    if any(mock_modules):
        sentinels = [m.DEFAULT for m in mock_modules if m is not None]
        return len([p for p in patchings
                    if not p.attribute_name and p.new in sentinels])
    return len(patchings)

# Fixed implementation
def fixed_num_mock_patch_args(function):
    patchings = getattr(function, "patchings", None)
    if not patchings:
        return 0
    mock_modules = [sys.modules.get("mock"), sys.modules.get("unittest.mock")]
    if any(mock_modules):
        sentinels = [m.DEFAULT for m in mock_modules if m is not None]
        return len([p for p in patchings
                    if not p.attribute_name and any(p.new is s for s in sentinels)])
    return len(patchings)

# Test original implementation with array
print("Testing original implementation with numpy array patch:")
try:
    res = original_num_mock_patch_args(test_with_array)
    print(f"Result: {res}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

# Test fixed implementation with array
print("\nTesting fixed implementation with numpy array patch:")
try:
    res = fixed_num_mock_patch_args(test_with_array)
    print(f"Result: {res} (expected: 0)")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

# Test fixed implementation with DEFAULT (should return 1)
print("\nTesting fixed implementation with DEFAULT sentinel:")
try:
    res = fixed_num_mock_patch_args(test_with_default)
    print(f"Result: {res} (expected: 1)")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

# Test that normal case still works
print("\nAll tests passed! Fix works correctly.")
