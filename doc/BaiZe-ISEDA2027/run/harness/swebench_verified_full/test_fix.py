import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.dates import AutoDateFormatter, DateFormatter

np.random.seed(1)
matplotlib.rcParams["text.usetex"] = True

dates = pd.date_range("2020-01-01 00:00:00", end="2020-01-01 00:10:00", periods=100)
data = np.random.rand(100)

# Test 1: Default formatter (what's broken)
fig, ax = plt.subplots(constrained_layout=True)
ax.plot(dates, data)
fig.canvas.draw()
print("=== Default formatter ===")
for tick in ax.xaxis.get_major_ticks():
    print(f"Label: {tick.label1.get_text()}, Width: {tick.label1.get_window_extent().width}")
plt.savefig("test_default.png")
plt.close()

# Test 2: Explicit DateFormatter without math mode
fig, ax = plt.subplots(constrained_layout=True)
ax.plot(dates, data)
ax.xaxis.set_major_formatter(DateFormatter("%d %H:%M"))
fig.canvas.draw()
print("\n=== Explicit DateFormatter ===")
for tick in ax.xaxis.get_major_ticks():
    print(f"Label: {tick.label1.get_text()}, Width: {tick.label1.get_window_extent().width}")
plt.savefig("test_explicit_formatter.png")
plt.close()
