import matplotlib
matplotlib.use('module://matplotlib_inline.backend_inline')
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

print(f"Matplotlib version: {matplotlib.__version__}")

fig, (ax, ax2) = plt.subplots(1, 2, figsize=[5.5, 2.8])
axins = inset_axes(ax, width=1.3, height=0.9)
# Try to render as inline backend does
print("Attempting to save with bbox_inches='tight' (what inline backend uses)...")
plt.savefig('/tmp/test_inset.png', bbox_inches='tight', dpi=100)
print("Success! No error.")
plt.close()
