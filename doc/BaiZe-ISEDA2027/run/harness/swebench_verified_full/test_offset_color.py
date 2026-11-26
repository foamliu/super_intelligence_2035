import matplotlib.pyplot as plt
import os

plt.rcParams.update({'ytick.labelcolor': 'red', 'ytick.color': 'black'})
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
ax.plot([1.01e9,1.02e9,1.03e9])

# Save the figure
plt.savefig('test_offset_color.png')
print("Saved figure to test_offset_color.png")

# Check the offset text color
offset_text = ax.yaxis.get_offset_text()
print(f"Offset text color: {offset_text.get_color()}")
print(f"Expected: red, Actual: {offset_text.get_color()}")
assert offset_text.get_color() == 'red', f"Offset text color is {offset_text.get_color()}, expected red"
print("Test passed!")
