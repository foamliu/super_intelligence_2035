import numpy as np
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, sharex=True, sharey=True)

print("Before clear():")
for i, ax in enumerate(axes.flatten()):
    print(f"Axes {i}:")
    print(f"  x tick labels visible: {ax.get_xticklabels()[0].get_visible()}")
    print(f"  y tick labels visible: {ax.get_yticklabels()[0].get_visible()}")
    print(f"  top spine visible: {ax.spines['top'].get_visible()}")
    print(f"  right spine visible: {ax.spines['right'].get_visible()}")

x = np.arange(0.0, 2*np.pi, 0.01)
y = np.sin(x)

for ax in axes.flatten():
    ax.clear()
    ax.plot(x, y)

print("\nAfter clear():")
for i, ax in enumerate(axes.flatten()):
    print(f"Axes {i}:")
    print(f"  x tick labels visible: {ax.get_xticklabels()[0].get_visible()}")
    print(f"  y tick labels visible: {ax.get_yticklabels()[0].get_visible()}")
    print(f"  top spine visible: {ax.spines['top'].get_visible()}")
    print(f"  right spine visible: {ax.spines['right'].get_visible()}")

plt.savefig("test_tick_visibility.png")
print("\nSaved figure to test_tick_visibility.png")
