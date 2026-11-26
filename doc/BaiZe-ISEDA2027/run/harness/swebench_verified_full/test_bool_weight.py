import numpy as np
import xarray as xr

dta = xr.DataArray([1., 1., 1.])
wgt = xr.DataArray(np.array([1, 1, 0], dtype=np.bool_))

result = dta.weighted(wgt).mean()
print(f"Result: {result}")
print(f"Expected: 1.0")
print(f"Match: {result.item() == 1.0}")

# Let's also check the sum of weights
sum_weights = xr.dot(dta.notnull(), wgt)
print(f"\nSum of weights (dot product): {sum_weights}")
print(f"Type: {type(sum_weights.item())}")
print(f"Value as int: {int(sum_weights.item())}")
