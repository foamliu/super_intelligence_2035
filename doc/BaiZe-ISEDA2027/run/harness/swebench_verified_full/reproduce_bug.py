import numpy as np
import matplotlib.colors as colors

# Create the data like in test_huge_range_log
x = -1
data = np.full((5, 5), x, dtype=np.float64)
data[0:2, :] = 1E20

# Create masked array like in image.py
mask = data < 1  # because vmin is 1
resampled_masked = np.ma.masked_array(data, mask)
print("resampled_masked:")
print(resampled_masked)

# Create LogNorm like in the test
norm = colors.LogNorm(vmin=1, vmax=data.max())
print(f"\nvmin: {norm.vmin}, vmax: {norm.vmax}")
print(f"clip: {norm.clip}")

# Try to apply norm
try:
    res = norm(resampled_masked)
    print("\nSuccess! Result:")
    print(res)
except ValueError as e:
    print(f"\nError: {e}")
    
# Wait, what if we look at what happens to t_vmin and t_vmax?
print(f"\ntransform([vmin, vmax]): {norm._trf.transform([norm.vmin, norm.vmax])}")
print(f"Are they finite? {np.isfinite(norm._trf.transform([norm.vmin, norm.vmax])).all()}")

# What if we process the value first?
val, is_scalar = norm.process_value(resampled_masked)
print(f"\nProcessed value type: {type(val)}")
print(f"Processed value mask: {val.mask}")

# What if we transform the value?
t_val = norm._trf.transform(val)
print(f"\nTransformed value: {t_val}")
