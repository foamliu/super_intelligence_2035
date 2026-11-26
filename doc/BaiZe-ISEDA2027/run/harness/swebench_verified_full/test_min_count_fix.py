import xarray as xr

# Test the exact case from the issue
da = xr.DataArray([[1., 2, 3], [4, 5, 6]])
print("Testing sum with multiple dimensions and min_count=1...")
result = da.sum(["dim_0", "dim_1"], min_count=1)
print(f"Result: {result}")
print(f"Value: {result.item()}")

# Test with all NaN values
da_nan = xr.DataArray([[np.nan, np.nan], [np.nan, np.nan]])
print("\nTesting sum with all NaN values, min_count=1...")
result_nan = da_nan.sum(["dim_0", "dim_1"], min_count=1)
print(f"Result: {result_nan}")
print(f"Is NaN: {np.isnan(result_nan.item())}")

# Test with some NaN values, enough valid
da_some_nan = xr.DataArray([[1, np.nan], [3, 4]])
print("\nTesting sum with some NaN values, min_count=2...")
result_some = da_some_nan.sum(["dim_0", "dim_1"], min_count=2)
print(f"Result: {result_some}")
print(f"Value: {result_some.item()}")

# Test with not enough valid
print("\nTesting sum with only 1 valid value, min_count=2...")
da_few = xr.DataArray([[1, np.nan], [np.nan, np.nan]])
result_few = da_few.sum(["dim_0", "dim_1"], min_count=2)
print(f"Result: {result_few}")
print(f"Is NaN: {np.isnan(result_few.item())}")
