import xarray as xr
import numpy as np

good_indexed, bad_indexed = xr.DataArray([None]), xr.DataArray([None])

class HasValues(object):
    values = 5
    
good_indexed.loc[{'dim_0': 0}] = set()
bad_indexed.loc[{'dim_0': 0}] = HasValues()

print("good_indexed.values:", good_indexed.values)
print("bad_indexed.values:", bad_indexed.values)
print("Expected bad_indexed.values to contain HasValues instance, not array(5)")
