import sys
sys.path.insert(0, '/tmp/xarray')
import numpy as np
import xarray as xr
from numpy.testing import assert_allclose

def test_boolean_weights():
    """Test that boolean weights work correctly for weighted mean"""
    # Original bug case
    dta = xr.DataArray([1., 1., 1.])
    wgt = xr.DataArray(np.array([1, 1, 0], dtype=np.bool_))
    result = dta.weighted(wgt).mean()
    assert_allclose(result.item(), 1.0)
    
    # Test with integer data
    dta_int = xr.DataArray([2, 4, 6])
    wgt_bool = xr.DataArray([True, False, True])
    result_int = dta_int.weighted(wgt_bool).mean()
    assert_allclose(result_int.item(), 4.0)
    
    # Test with all True weights
    dta_all = xr.DataArray([1, 2, 3, 4])
    wgt_all = xr.DataArray([True, True, True, True])
    result_all = dta_all.weighted(wgt_all).mean()
    assert_allclose(result_all.item(), 2.5)
    
    # Test with some False weights
    dta_some = xr.DataArray([10, 20, 30, 40])
    wgt_some = xr.DataArray([True, False, False, True])
    result_some = dta_some.weighted(wgt_some).mean()
    assert_allclose(result_some.item(), 25.0)
    
    # Test with NaN values in data
    dta_nan = xr.DataArray([1., np.nan, 3., 4.])
    wgt_nan = xr.DataArray([True, True, False, True])
    result_nan = dta_nan.weighted(wgt_nan).mean(skipna=True)
    assert_allclose(result_nan.item(), 2.5)  # (1*1 + 4*1) / (1+1) = 2.5
    
    print("All boolean weight tests passed!")

if __name__ == "__main__":
    test_boolean_weights()
