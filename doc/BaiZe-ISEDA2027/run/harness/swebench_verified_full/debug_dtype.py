
import numpy as np

ii, jj = np.ogrid[:100, :100]
im = (ii+jj) % 20 < 10
z_dtype = im.dtype

print(f"z_dtype: {z_dtype}")
print(f"np.issubdtype(z_dtype, bool): {np.issubdtype(z_dtype, bool)}")
print(f"np.issubdtype(z_dtype, np.bool_): {np.issubdtype(z_dtype, np.bool_)}")
print(f"z_dtype == bool: {z_dtype == bool}")
