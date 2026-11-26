import matplotlib.pyplot as plt
import os

fig = plt.figure()
ax = fig.add_subplot(1,1,1)
ax.plot([1.01e9,1.02e9,1.03e9])

# Set tick label color explicitly on the axis
ax.tick_params(axis='y', labelcolor='green', color='black')

# Save the figure
plt.savefig('test_offset_color_explicit.png')
print("Saved figure to test_offset_color_explicit.png")

# Check the offset text color
offset_text = ax.yaxis.get_offset_text()
print(f"Offset text color: {offset_text.get_color()}")
print(f"Expected: green, Actual: {offset_text.get_color()}")
assert offset_text.get_color() == 'green', f"Offset text color is {offset_text.get_color()}, expected green"
print("Explicit setting test passed!")
