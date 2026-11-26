import sys
sys.path.insert(0, '/tmp/xarray')
import numpy as np
import xarray as xr

# Test all zero weights
dta = xr.DataArray([1, 2, 3])
wgt = xr.DataArray([False, False, False])
result = dta.weighted(wgt).mean()
print(f"All zero boolean weights: mean = {result} (expected NaN)")
print(f"Is NaN: {np.isnan(result.item())}")

# Test single element
dta_single = xr.DataArray([5.0])
wgt_single = xr.DataArray([True])
result_single = dta_single.weighted(wgt_single).mean()
print(f"\nSingle element, True weight: mean = {result_single} (expected 5.0)")
print(f"Match: {result_single.item() == 5.0}")

# Test multi-dimensional array
dta_2d = xr.DataArray([[1, 2, 3], [4, 5, 6]], dims=['x', 'y'])
wgt_2d = xr.DataArray([[True, False, True], [False, True, False]], dims=['x', 'y'])
result_2d = dta_2d.weighted(wgt_2d).mean(dim='y')
print(f"\n2D array, boolean weights, mean over y: {result_2d.values} (expected [2.0, 5.0])")
print(f"Match: {np.allclose(result_2d.values, [2.0, 5.0])}")
