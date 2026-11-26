import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.dates import AutoDateFormatter

np.random.seed(1)

dates = pd.date_range("2020-01-01 00:00:00", end="2020-01-01 00:10:00", periods=100)
data = np.random.rand(100)

# Test with usetex True
matplotlib.rcParams["text.usetex"] = True
fig, ax = plt.subplots(constrained_layout=True)
ax.plot(dates, data)
fig.canvas.draw()
print("=== With usetex=True ===")
for tick in ax.xaxis.get_major_ticks():
    label = tick.label1
    print(f"Label: {label.get_text()}, Width: {label.get_window_extent().width}, Bbox: {label.get_window_extent()}")
plt.savefig("test_usetex_true.png")
plt.close()

# Test with usetex False
matplotlib.rcParams["text.usetex"] = False
fig, ax = plt.subplots(constrained_layout=True)
ax.plot(dates, data)
fig.canvas.draw()
print("\n=== With usetex=False ===")
for tick in ax.xaxis.get_major_ticks():
    label = tick.label1
    print(f"Label: {label.get_text()}, Width: {label.get_window_extent().width}, Bbox: {label.get_window_extent()}")
plt.savefig("test_usetex_false.png")
plt.close()
