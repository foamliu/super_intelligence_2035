import matplotlib
matplotlib.use('Agg') # Non-interactive backend
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

fig, (ax, ax2) = plt.subplots(1, 2, figsize=[5.5, 2.8])
axins = inset_axes(ax, width=1.3, height=0.9)
# Simulate what the inline backend does: save with bbox_inches='tight'
plt.savefig('/tmp/test_fixed.png', bbox_inches='tight', dpi=100)
print("✅ Fixed: No AttributeError! The inset axes was created successfully.")
plt.close()
