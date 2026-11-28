"""Test for polyval with timedelta64 and datetime64 coordinates"""
import numpy as np
import xarray as xr

# Test case from the issue
values = np.array(
    [
        "2021-04-01T05:25:19.000000000",
        "2021-04-01T05:25:29.000000000",
        "2021-04-01T05:25:39.000000000",
        "2021-04-01T05:25:49.000000000",
        "2021-04-01T05:25:59.000000000",
        "2021-04-01T05:26:09.000000000",
    ],
    dtype="datetime64[ns]",
)

# Test 1: timedelta coordinate
td_coord = xr.DataArray(values - values[0], dims="azimuth_time", name="azimuth_time")
polyfit_coefficients = xr.DataArray(
    [
        [2.33333335e-43, 1.62499999e-43, 2.79166678e-43],
        [-1.15316667e-30, 1.49518518e-31, 9.08833333e-31],
        [-2.50272583e-18, -1.23851062e-18, -2.99098229e-18],
        [5.83965193e-06, -1.53321770e-07, -4.84640242e-06],
        [4.44739216e06, 1.45053974e06, 5.29960857e06],
    ],
    dims=("degree", "axis"),
    coords={"axis": [0, 1, 2], "degree": [4, 3, 2, 1, 0]},
)

result_td = xr.polyval(td_coord, polyfit_coefficients)
expected_first_row = [4447392.16, 1450539.74, 5299608.57]
assert np.allclose(result_td.isel(azimuth_time=0), expected_first_row), f"First row mismatch: {result_td.isel(azimuth_time=0)} vs {expected_first_row}"
print("✓ Timedelta coordinate test passed")

# Test 2: datetime data with timedelta coordinate (original user case)
da = xr.DataArray(values, dims="azimuth_time", coords={"azimuth_time": values - values[0]})
result_dt = xr.polyval(da, polyfit_coefficients)
# When using offset=None, this should also give the same result as timedelta
# Because datetime_to_numeric uses min(da) as offset, so values are same as td_coord
assert np.allclose(result_dt.isel(azimuth_time=0), expected_first_row), f"First row mismatch: {result_dt.isel(azimuth_time=0)} vs {expected_first_row}"
print("✓ Datetime DataArray test passed")

print("All tests passed!")
