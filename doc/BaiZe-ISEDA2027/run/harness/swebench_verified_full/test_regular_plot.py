import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.rcParams["text.usetex"] = True

x = np.arange(3)
y = np.random.rand(3)

fig, ax = plt.subplots()
ax.bar(x, y)
ax.set_xticks(x)
ax.set_xticklabels(["01 00:00", "01 00:05", "01 00:10"])
fig.canvas.draw()

for tick in ax.xaxis.get_major_ticks():
    print(f"Label: {tick.label1.get_text()}, Width: {tick.label1.get_window_extent().width}")

plt.savefig("test_regular_plot.png")
