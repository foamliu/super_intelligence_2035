import numpy as np
import astropy.wcs
from astropy.coordinates import SkyCoord
import astropy.units as u

# Create the WCS as per the user's example
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

# Test full WCS world_to_pixel
pt = SkyCoord(Tx=0*u.arcsec, Ty=0*u.arcsec, frame=astropy.wcs.utils.wcs_to_celestial_frame(fits_wcs))
full_result = fits_wcs.world_to_pixel(pt, 1.05*u.angstrom)
print("Full WCS world_to_pixel result:", full_result)

# Test sliced WCS
ll_sliced_wcs = astropy.wcs.wcsapi.SlicedLowLevelWCS(fits_wcs, 0)
hl_sliced_wcs = astropy.wcs.wcsapi.HighLevelWCSWrapper(ll_sliced_wcs)
sliced_result = hl_sliced_wcs.world_to_pixel(pt)
print("Sliced WCS world_to_pixel result:", sliced_result)

# Also confirm pixel_to_world works
px, py, pz = full_result
full_p2w = fits_wcs.pixel_to_world(px, py, pz)
print("\nFull WCS pixel_to_world result:", full_p2w)
sliced_p2w = hl_sliced_wcs.pixel_to_world(px, py)
print("Sliced WCS pixel_to_world result:", sliced_p2w)
