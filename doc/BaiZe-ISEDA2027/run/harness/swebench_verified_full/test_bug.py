import numpy as np

# Simulate sentinels (mock.DEFAULT objects)
DEFAULT1 = object()
DEFAULT2 = object()
sentinels = [DEFAULT1, DEFAULT2]

# Test with numpy array
new_val = np.array([-5.5, 3.0])

# This is the problematic check
try:
    result = new_val in sentinels
    print(f"Result: {result}")
except ValueError as e:
    print(f"Error: {type(e).__name__}: {e}")
    print("This is the bug!")
