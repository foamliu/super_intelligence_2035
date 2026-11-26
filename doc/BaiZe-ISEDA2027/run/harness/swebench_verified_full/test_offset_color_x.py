import matplotlib.pyplot as plt
import os

plt.rcParams.update({'xtick.labelcolor': 'blue', 'xtick.color': 'black'})
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
ax.plot([1, 2, 3], [1.01e9,1.02e9,1.03e9])

# Save the figure
plt.savefig('test_offset_color_x.png')
print("Saved figure to test_offset_color_x.png")

# Check the offset text color
offset_text = ax.xaxis.get_offset_text()
print(f"X Offset text color: {offset_text.get_color()}")
print(f"Expected: blue, Actual: {offset_text.get_color()}")
assert offset_text.get_color() == 'blue', f"Offset text color is {offset_text.get_color()}, expected blue"
print("X axis test passed!")
