import numpy as np
import matplotlib.colors as colors

# Test what happens when all values are masked
data = np.full((5, 5), -1, dtype=np.float64)
mask = data < 1
resampled_masked = np.ma.masked_array(data, mask)
print("All masked resampled_masked:")
print(resampled_masked)

# Create LogNorm with explicit vmin and vmax
norm = colors.LogNorm(vmin=1, vmax=1e20)
print(f"\nvmin: {norm.vmin}, vmax: {norm.vmax}")

# Test applying norm
try:
    res = norm(resampled_masked)
    print("\nSuccess with all masked! Result:")
    print(res)
except ValueError as e:
    print(f"\nError with all masked: {e}")

# Now test if autoscale_None gets called even when vmin/vmax are set
print("\n--- Testing autoscale_None with all masked ---")
norm2 = colors.LogNorm(vmin=1, vmax=1e20)
norm2.autoscale_None(resampled_masked)
print(f"After autoscale_None: vmin={norm2.vmin}, vmax={norm2.vmax}")
print(f"Type vmin: {type(norm2.vmin)}, Type vmax: {type(norm2.vmax)}")

# What if we transform these?
print(f"\nTransform vmin/vmax: {norm2._trf.transform([norm2.vmin, norm2.vmax])}")
print(f"Are finite: {np.isfinite(norm2._trf.transform([norm2.vmin, norm2.vmax])).all()}")

# Wait, what if vmin is a masked scalar?
vmin_masked = np.ma.masked
print(f"\nTransform masked vmin: {norm._trf.transform([vmin_masked, 1e20])}")
