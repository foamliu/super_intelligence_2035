
import sys
sys.path.insert(0, '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/xarray')

import xarray as xr
from xarray.structure.merge import merge

print("Testing merge with combine_attrs='override'...")
xds1 = xr.Dataset(attrs={'a':'b'})
xds2 = xr.Dataset(attrs={'a':'c'})
print(f"Initial: a1: {xds1.attrs['a']}, a2: {xds2.attrs['a']}")

xds3 = merge([xds1, xds2], combine_attrs='override')
print(f"After merge: a1: {xds1.attrs['a']}, a2: {xds2.attrs['a']}, a3: {xds3.attrs['a']}")

xds3.attrs['a'] = 'd'
print(f"After changing xds3: a1: {xds1.attrs['a']}, a2: {xds2.attrs['a']}, a3: {xds3.attrs['a']}")

print("\n✅ Test passed! Original xds1 was not modified." if xds1.attrs['a'] == 'b' else "\n❌ Test FAILED! Original xds1 was modified.")
