import matplotlib.pyplot as plt
import pickle
import numpy as np

# Test basic pickling functionality
fig = plt.figure(dpi=150)
ax = fig.add_subplot(111)
x = np.linspace(0, 10, 100)
y = np.sin(x)
ax.plot(x, y)
ax.set_title("Test Pickle")
ax.set_xlabel("X")
ax.set_ylabel("Y")

# Pickle and unpickle
with open("test_basic.pickle", "wb") as f:
    pickle.dump(fig, f)

with open("test_basic.pickle", "rb") as f:
    fig2 = pickle.load(f)

# Check that the figure properties are preserved
assert fig2.dpi == 150, f"Expected DPI 150, got {fig2.dpi}"
assert len(fig2.axes) == 1, f"Expected 1 axes, got {len(fig2.axes)}"
ax2 = fig2.axes[0]
assert ax2.get_title() == "Test Pickle", f"Title mismatch"
assert ax2.get_xlabel() == "X", f"X label mismatch"
assert ax2.get_ylabel() == "Y", f"Y label mismatch"

# Check that plotting still works
fig2.savefig("test_pickle_output.png")
print("✅ Basic pickling works correctly!")

# Clean up
import os
os.remove("test_basic.pickle")
os.remove("test_pickle_output.png")
