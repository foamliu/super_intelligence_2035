import numpy as np
import xarray as xr

# Test case 1: All non-nan values
da = xr.DataArray([[1., 2, 3], [4, 5, 6]])
result = da.sum(["dim_0", "dim_1"], min_count=1)
assert result == 21.0, f"Expected 21.0, got {result}"
print("✓ Test 1 passed: All non-nan values sum correctly")

# Test case 2: All nan values
da_nan = xr.DataArray([[np.nan, np.nan], [np.nan, np.nan]])
result_nan = da_nan.sum(["dim_0", "dim_1"], min_count=1)
assert np.isnan(result_nan), f"Expected nan, got {result_nan}"
print("✓ Test 2 passed: All nan values return nan with min_count=1")

# Test case 3: Some nan values, enough valid
da_some_nan = xr.DataArray([[1., np.nan, 3], [4, 5, np.nan]])
result_some = da_some_nan.sum(["dim_0", "dim_1"], min_count=2)
assert result_some == 13.0, f"Expected 13.0, got {result_some}"
print("✓ Test 3 passed: Enough valid values return correct sum")

# Test case 4: Not enough valid values
da_few = xr.DataArray([[1., np.nan, np.nan], [np.nan, np.nan, np.nan]])
result_few = da_few.sum(["dim_0", "dim_1"], min_count=2)
assert np.isnan(result_few), f"Expected nan, got {result_few}"
print("✓ Test 4 passed: Not enough valid values return nan")

# Test case 5: 3D array, sum over two dimensions
da_3d = xr.DataArray(np.ones((2, 3, 4)))
da_3d[0, :, :] = np.nan
result_3d = da_3d.sum(dim=["dim_0", "dim_1"], min_count=3)
expected = np.full(4, 3.0)
np.testing.assert_allclose(result_3d, expected)
print("✓ Test 5 passed: 3D array sum over two dimensions works")

print("\n✅ All tests passed! The min_count with multiple dimensions fix is working correctly.")
