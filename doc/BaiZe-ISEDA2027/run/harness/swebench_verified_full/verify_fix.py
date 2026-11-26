import numpy as np

# Let's simulate the logic
def simulate_maybe_null_out(axis, mask_shape, min_count=1):
    # Old buggy code: would fail if axis is a list/tuple
    try:
        old = mask_shape[axis] - 0 - min_count < 0
        print(f"Old code with axis={axis} worked: {old}")
    except Exception as e:
        print(f"Old code with axis={axis} failed: {e}")
    
    # New fixed code
    new = np.take(mask_shape, axis).prod() - 0 - min_count < 0
    print(f"New code with axis={axis} worked: {new}")

# Test cases
print("Test 1: single axis")
simulate_maybe_null_out(0, (2, 3))

print("\nTest 2: multiple axes (the bug case)")
simulate_maybe_null_out([0, 1], (2, 3))

print("\nTest 3: multiple axes with tuple")
simulate_maybe_null_out((0, 1), (2, 3, 4))
