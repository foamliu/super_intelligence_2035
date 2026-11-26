import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter

np.random.seed(1)
matplotlib.rcParams["text.usetex"] = True

dates = pd.date_range("2020-01-01 00:00:00", end="2020-01-01 00:10:00", periods=100)
data = np.random.rand(100)

# Custom formatter that returns plain text, not wrapped in math mode
class CustomDateFormatter(DateFormatter):
    def format_data(self, value):
        fmt = self._formatter.segmentFromData(value)
        return fmt.strftime(self.fmt)
    
fig, ax = plt.subplots(constrained_layout=True)
ax.plot(dates, data)
ax.xaxis.set_major_formatter(CustomDateFormatter("%d %H:%M"))
fig.canvas.draw()

print("=== Custom formatter (no math mode) ===")
for tick in ax.xaxis.get_major_ticks():
    print(f"Label: {tick.label1.get_text()}, Width: {tick.label1.get_window_extent().width}")

plt.savefig("test_custom_formatter_fix.png")
