import numpy as np
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, sharex=True, sharey=True)
fig.canvas.draw() # Force drawing to populate ticks

print("Before clear():")
for i, ax in enumerate(axes.flatten()):
    print(f"Axes {i}:")
    xtick_vis = any([t.get_visible() for t in ax.get_xticklabels()])
    ytick_vis = any([t.get_visible() for t in ax.get_yticklabels()])
    print(f"  Any x tick labels visible: {xtick_vis}")
    print(f"  Any y tick labels visible: {ytick_vis}")
    print(f"  Top ticks visible: {ax.tick_params(axis='x', which='both', top=None)['top'][0]}")
    print(f"  Right ticks visible: {ax.tick_params(axis='y', which='both', right=None)['right'][0]}")

x = np.arange(0.0, 2*np.pi, 0.01)
y = np.sin(x)

for ax in axes.flatten():
    ax.clear()
    ax.plot(x, y)

fig.canvas.draw() # Force drawing to populate ticks again

print("\nAfter clear():")
for i, ax in enumerate(axes.flatten()):
    print(f"Axes {i}:")
    xtick_vis = any([t.get_visible() for t in ax.get_xticklabels()])
    ytick_vis = any([t.get_visible() for t in ax.get_yticklabels()])
    print(f"  Any x tick labels visible: {xtick_vis}")
    print(f"  Any y tick labels visible: {ytick_vis}")
    # Check tick params for top/right ticks
    params = ax.tick_params(axis='both', which='both', top=None, right=None, labeltop=None, labelright=None)
    print(f"  Top ticks visible: {params['top'][0]}")
    print(f"  Right ticks visible: {params['right'][0]}")

plt.savefig("test_tick_visibility_fixed.png")
print("\nSaved figure to test_tick_visibility_fixed.png")
