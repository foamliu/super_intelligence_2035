import sys
sys.path.insert(0, "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/xarray")

import numpy as np
from xarray.coding.variables import _convert_unsigned_fill_value

# Test the case mentioned in the issue
# Simulate what pydap returns: uint8 data with _Unsigned=False attribute
data = np.array([128, 255, 0, 1, 2, np.nan, 127], dtype=np.uint8)
# Wait, but np.nan can't be in uint8, so maybe pydap converts to float?
data_float = np.array([128.0, 255.0, 0.0, 1.0, 2.0, np.nan, 127.0], dtype=np.float32)

print("Testing with uint8 data:")
result = _convert_unsigned_fill_value("test", data, "false", None, set())
print(f"Input: {data}")
print(f"Output: {result}")
print(f"Output dtype: {result.dtype}")

print("\nTesting with float32 data:")
try:
    result_float = _convert_unsigned_fill_value("test", data_float, "false", None, set())
    print(f"Input: {data_float}")
    print(f"Output: {result_float}")
    print(f"Output dtype: {result_float.dtype}")
except Exception as e:
    print(f"Error: {e}")