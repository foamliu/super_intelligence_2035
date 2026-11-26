import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams["text.usetex"] = True

fig, ax = plt.subplots()
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

# Add a regular text label
text = ax.text(0.5, 0.5, "01 00:00", fontsize=10)
fig.canvas.draw()

print(f"Regular text label width: {text.get_window_extent().width}")
print(f"Text: {text.get_text()}")

# Add a math text label
math_text = ax.text(0.5, 0.25, r"$\mathdefault{01\;00{:}00}$", fontsize=10)
fig.canvas.draw()

print(f"\nMath text label width: {math_text.get_window_extent().width}")
print(f"Text: {math_text.get_text()}")

plt.savefig("test_text_widths.png")
