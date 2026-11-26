import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

np.random.seed(1)
matplotlib.rcParams["text.usetex"] = True
matplotlib.rcParams["axes.formatter.use_mathtext"] = False # This is the fix!

dates = pd.date_range("2020-01-01 00:00:00", end="2020-01-01 00:10:00", periods=100)
data = np.random.rand(100)

fig, ax = plt.subplots(constrained_layout=True)
ax.plot(dates, data)
fig.canvas.draw()

print("=== With use_mathtext=False ===")
for tick in ax.xaxis.get_major_ticks():
    print(f"Label: {tick.label1.get_text()}, Width: {tick.label1.get_window_extent().width}")

plt.savefig("test_rcparams_fix.png")
