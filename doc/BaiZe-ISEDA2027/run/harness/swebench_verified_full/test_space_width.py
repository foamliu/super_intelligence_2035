import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams["text.usetex"] = True

fig, ax = plt.subplots()
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

# Test with \;
text1 = ax.text(0.5, 0.75, r"$\mathdefault{01\;00{:}00}$", fontsize=10)
fig.canvas.draw()
print(f"With \\\\;: {text1.get_window_extent().width}")

# Test with regular space
text2 = ax.text(0.5, 0.5, r"$\mathdefault{01 00{:}00}$", fontsize=10)
fig.canvas.draw()
print(f"With regular space: {text2.get_window_extent().width}")

# Test with \thinspace
text3 = ax.text(0.5, 0.25, r"$\mathdefault{01\,00{:}00}$", fontsize=10)
fig.canvas.draw()
print(f"With \\\\,: {text3.get_window_extent().width}")

plt.savefig("test_space_widths.png")
