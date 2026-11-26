
import sys
# Add local matplotlib directory to path first
sys.path.insert(0, './matplotlib/lib')

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
print(f"Expected levels for boolean contour: [0.5]")
assert np.array_equal(contour1.levels, [0.5]), f"Expected levels [0.5], got {contour1.levels}"

# Test contour with levels=[.5]
contour2 = ax2.contour(im, levels=[.5])
ax2.set_title("contour(im, levels=[.5])")
print(f"contour levels with explicit levels=[.5]: {contour2.levels}")

# Test contourf with boolean array
fig2, ax3 = plt.subplots(1, 1, figsize=(5,5))
contourf1 = ax3.contourf(im)
ax3.set_title("contourf(im) (no levels)")
print(f"\ncontourf levels without explicit levels: {contourf1.levels}")
print(f"Expected levels for boolean contourf: [0. 0.5 1. ]")
assert np.allclose(contourf1.levels, [0, 0.5, 1]), f"Expected levels [0, 0.5, 1], got {contourf1.levels}"

# Test tricontour with boolean array
fig3, (ax4, ax5) = plt.subplots(1, 2, figsize=(10, 5))
x = np.random.rand(1000)
y = np.random.rand(1000)
z = (x + y) < 0.5  # boolean array
tricontour1 = ax4.tricontour(x, y, z)
ax4.set_title("tricontour(x,y,z) (no levels, z boolean)")
print(f"\ntricontour levels without explicit levels: {tricontour1.levels}")
assert np.array_equal(tricontour1.levels, [0.5]), f"Expected levels [0.5], got {tricontour1.levels}"

tricontourf1 = ax5.tricontourf(x, y, z)
ax5.set_title("tricontourf(x,y,z) (no levels, z boolean)")
print(f"tricontourf levels without explicit levels: {tricontourf1.levels}")
assert np.allclose(tricontourf1.levels, [0, 0.5, 1]), f"Expected levels [0, 0.5, 1], got {tricontourf1.levels}"

plt.savefig("test_local_contour_bool.png")
print("\n✅ All tests passed! The boolean auto-detection feature works correctly.")
print("   - contour(boolean_array) now defaults to levels=[0.5]")
print("   - contourf(boolean_array) now defaults to levels=[0, 0.5, 1]")
print("   - tricontour and tricontourf also work with boolean arrays")
