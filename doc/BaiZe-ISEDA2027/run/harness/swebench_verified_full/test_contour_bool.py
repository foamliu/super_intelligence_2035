
import numpy as np
import matplotlib.pyplot as plt

# Test case from the user
ii, jj = np.ogrid[:100, :100]
im = (ii+jj) % 20 < 10

print(f"im dtype: {im.dtype}")
print(f"im is boolean: {np.issubdtype(im.dtype, bool)}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

# Test contour without levels
contour1 = ax1.contour(im)
ax1.set_title("contour(im) (no levels)")
print(f"\ncontour levels without explicit levels: {contour1.levels}")

# Test contour with levels=[.5]
contour2 = ax2.contour(im, levels=[.5])
ax2.set_title("contour(im, levels=[.5])")
print(f"contour levels with explicit levels=[.5]: {contour2.levels}")

# Test contourf with boolean array
fig2, ax3 = plt.subplots(1, 1, figsize=(5,5))
contourf1 = ax3.contourf(im)
ax3.set_title("contourf(im) (no levels)")
print(f"\ncontourf levels without explicit levels: {contourf1.levels}")

plt.savefig("test_contour_bool.png")
print("\nSaved test figure to test_contour_bool.png")
