import sys
import os
sys.path.insert(0, '/tmp/xarray')

import numpy as np
import xarray as xr
from xarray.core.weighted import DataArrayWeighted

# Test case from the bug report
dta = xr.DataArray([1., 1., 1.])
wgt = xr.DataArray(np.array([1, 1, 0], dtype=np.bool_))

result = dta.weighted(wgt).mean()
print(f"Result after fix: {result}")
print(f"Expected: 1.0")
print(f"Match: {result.item() == 1.0}")

# Test sum of weights
wrapped = DataArrayWeighted(dta, wgt)
mask = dta.notnull()
sum_weights = wrapped._reduce(mask.astype(float), wgt, dim=None, skipna=False)
print(f"\nSum of weights after fix: {sum_weights}")
print(f"Type: {type(sum_weights.item())}")

# Additional test cases
print("\n--- Additional test cases ---")

# Test with integer data and boolean weights
dta_int = xr.DataArray([2, 4, 6])
wgt_bool = xr.DataArray([True, False, True])
result_int = dta_int.weighted(wgt_bool).mean()
print(f"Integer data, boolean weights: mean = {result_int} (expected 4.0)")
print(f"Match: {result_int.item() == 4.0}")

# Test with float weights
wgt_float = xr.DataArray([0.5, 0.3, 0.2])
result_float = dta.weighted(wgt_float).mean()
print(f"Float weights: mean = {result_float} (expected 1.0)")
print(f"Match: {result_float.item() == 1.0}")

# Test with some NaN values in data
dta_nan = xr.DataArray([1., np.nan, 3.])
wgt_nan = xr.DataArray([True, True, True])
result_nan = dta_nan.weighted(wgt_nan).mean(skipna=True)
print(f"Data with NaN, boolean weights: mean = {result_nan} (expected 2.0)")
print(f"Match: {result_nan.item() == 2.0}")
