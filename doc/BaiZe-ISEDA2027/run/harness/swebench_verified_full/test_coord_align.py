import sys
sys.path.insert(0, '/tmp/xarray')
import xarray as xr
import numpy as np

data = xr.DataArray([1,2,3,4], dims='a', coords={'a': [1,2,3,4]})
weights = xr.DataArray([0.1, 0.2, 0.3, 0.4], dims='a', coords={'a': [0,1,2,3]})
mask = data.notnull()

res1 = xr.dot(mask, weights, dims='a')
res2 = xr.dot(mask.astype(float), weights, dims='a')

print("dot(mask, weights) value:", res1.item())
print("dot(mask.astype(float), weights) value:", res2.item())
print("Are equal?", np.isclose(res1.item(), res2.item()))

