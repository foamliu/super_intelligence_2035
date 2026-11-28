import numpy as np
import astropy.wcs
from astropy.coordinates import SkyCoord
import astropy.units as u
from astropy.wcs.wcsapi import SlicedLowLevelWCS, HighLevelWCSWrapper

# Test case from the issue
nx = 100
ny = 25
nz = 2
wcs_header = {
    'WCSAXES': 3,
    'CRPIX1': (nx + 1)/2,
    'CRPIX2': (ny + 1)/2,
    'CRPIX3': 1.0,
    'PC1_1': 0.0,
    'PC1_2': -1.0,
    'PC1_3': 0.0,
    'PC2_1': 1.0,
    'PC2_2': 0.0,
    'PC2_3': -1.0,
    'CDELT1': 5,
    'CDELT2': 5,
    'CDELT3': 0.055,
    'CUNIT1': 'arcsec',
    'CUNIT2': 'arcsec',
    'CUNIT3': 'Angstrom',
    'CTYPE1': 'HPLN-TAN',
    'CTYPE2': 'HPLT-TAN',
    'CTYPE3': 'WAVE',
    'CRVAL1': 0.0,
    'CRVAL2': 0.0,
    'CRVAL3': 1.05,

}
fits_wcs = astropy.wcs.WCS(header=wcs_header)

print("Testing unsliced WCS:")
pt = SkyCoord(Tx=0*u.arcsec, Ty=0*u.arcsec, frame=astropy.wcs.utils.wcs_to_celestial_frame(fits_wcs))
result = fits_wcs.world_to_pixel(pt, 1.05*u.angstrom)
print(f"world_to_pixel result: {result}")
expected_x, expected_y = result[0], result[1]
print(f"Expected x={expected_x}, y={expected_y} for sliced WCS")

print("\nTesting sliced WCS:")
ll_sliced_wcs = SlicedLowLevelWCS(fits_wcs, 0)
hl_sliced_wcs = HighLevelWCSWrapper(ll_sliced_wcs)
result_sliced = hl_sliced_wcs.world_to_pixel(pt)
print(f"world_to_pixel result: {result_sliced}")

# Check if results match
x_match = np.allclose(result_sliced[0], expected_x, atol=1e-10)
y_match = np.allclose(result_sliced[1], expected_y, atol=1e-10)

print(f"\nX coordinate matches: {x_match}")
print(f"Y coordinate matches: {y_match}")
print(f"Test {'PASSED' if x_match and y_match else 'FAILED'}")