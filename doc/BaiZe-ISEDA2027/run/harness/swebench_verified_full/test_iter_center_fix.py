
"""Test case for the center=True rolling iteration bug fix."""
import numpy as np
import xarray as xr


def test_rolling_iter_center():
    """Test that manual iteration over center=True rolling windows gives same result as builtin mean."""
    my_data = xr.DataArray(np.arange(1, 10), dims="x")
    
    # Builtin result
    result_builtin = my_data.rolling(x=3, center=True).mean()
    
    # Manual iteration result
    result_iter = xr.DataArray(
        [window.mean().item() for _, window in my_data.rolling(x=3, center=True)],
        dims="x",
        coords=my_data.coords
    )
    
    # Verify they are equal
    xr.testing.assert_allclose(result_builtin, result_iter)
    print("✅ Test passed: iteration with center=True matches builtin mean!")
    print(f"Builtin: {result_builtin.values}")
    print(f"Iterated: {result_iter.values}")
    
    # Test even window size
    my_data2 = xr.DataArray(np.arange(1, 11), dims="x")
    result_builtin2 = my_data2.rolling(x=4, center=True).mean()
    result_iter2 = xr.DataArray(
        [window.mean().item() for _, window in my_data2.rolling(x=4, center=True)],
        dims="x",
        coords=my_data2.coords
    )
    xr.testing.assert_allclose(result_builtin2, result_iter2)
    print("\n✅ Test passed for even window size (4):")
    print(f"Builtin: {result_builtin2.values}")
    print(f"Iterated: {result_iter2.values}")
    
    # Test center=False (should still work as before)
    result_builtin_false = my_data.rolling(x=3, center=False).mean()
    result_iter_false = xr.DataArray(
        [window.mean().item() for _, window in my_data.rolling(x=3, center=False)],
        dims="x",
        coords=my_data.coords
    )
    xr.testing.assert_allclose(result_builtin_false, result_iter_false)
    print("\n✅ Test passed: center=False still works correctly!")
    print(f"Builtin: {result_builtin_false.values}")
    print(f"Iterated: {result_iter_false.values}")


if __name__ == "__main__":
    test_rolling_iter_center()
