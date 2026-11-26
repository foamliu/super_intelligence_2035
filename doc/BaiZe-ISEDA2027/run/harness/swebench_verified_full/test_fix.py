import numpy as np
import matplotlib.colors as colors

# Test the fix with all masked array
data = np.full((5, 5), -1, dtype=np.float64)
mask = np.ones_like(data, dtype=bool)  # All masked
resampled_masked = np.ma.masked_array(data, mask)

# Create LogNorm with vmin=1, vmax=1e20
norm = colors.LogNorm(vmin=1, vmax=1e20)
print(f"vmin={norm.vmin}, vmax={norm.vmax}")

# This used to raise ValueError("Invalid vmin or vmax")?
try:
    result = norm(resampled_masked)
    print("✓ No error raised!")
    print(f"Result is all masked: {result.mask.all()}")
except ValueError as e:
    print(f"✗ Error raised: {e}")

# Test with some valid values
data = np.full((5, 5), -1, dtype=np.float64)
data[0:2, :] = 1e20
mask = data < 1
resampled_masked = np.ma.masked_array(data, mask)
try:
    result = norm(resampled_masked)
    print("\n✓ No error raised with partial valid values!")
    print(f"Result shape: {result.shape}")
    print(f"Valid values: {result[~result.mask]}")
except ValueError as e:
    print(f"\n✗ Error raised with partial valid values: {e}")

# Test with invalid vmin
print("\n--- Testing with invalid vmin (0) ---")
norm_invalid = colors.LogNorm(vmin=0, vmax=1e20)
data = np.array([1, 10, 100])
try:
    result = norm_invalid(data)
    print("✓ No error raised! All masked? {np.ma.is_masked(result)}")
except ValueError as e:
    print(f"✗ Error raised: {e}")
