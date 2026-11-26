import numpy as np
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, sharex=True, sharey=True)

x = np.arange(0.0, 2*np.pi, 0.01)
y = np.sin(x)

for ax in axes.flatten():
    ax.clear()
    ax.plot(x, y)

plt.savefig("test_shared_clear.png")
print("Saved figure to test_shared_clear.png")
