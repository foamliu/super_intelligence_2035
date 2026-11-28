import xarray as xr
import numpy as np

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
azimuth_time = xr.DataArray(
    values, name="azimuth_time", coords={"azimuth_time": values - values[0]}
)

print("azimuth_time data dtype:", azimuth_time.dtype)
print("azimuth_time coord dtype:", azimuth_time.coords["azimuth_time"].dtype)

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

print("\nTesting polyval with azimuth_time (data is datetime64):")
result = xr.polyval(azimuth_time, polyfit_coefficients)
print(result)

print("\nTesting polyval with azimuth_time coordinate (timedelta64):")
result2 = xr.polyval(azimuth_time.azimuth_time, polyfit_coefficients)
print(result2)

# Let's check what _ensure_numeric returns
from xarray.computation.computation import _ensure_numeric
print("\n_ensure_numeric(azimuth_time) dtype:", _ensure_numeric(azimuth_time).dtype)
print("_ensure_numeric(azimuth_time.azimuth_time) dtype:", _ensure_numeric(azimuth_time.azimuth_time).dtype)
