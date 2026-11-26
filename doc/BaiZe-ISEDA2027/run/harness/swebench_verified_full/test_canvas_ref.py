import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pickle

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot([0,1,2], [1,2,3], label="test")
leg = ax.legend()
leg.set_draggable(True)

print(f"Legend has _draggable: {hasattr(leg, '_draggable')}")
print(f"Draggable has canvas attribute: {hasattr(leg._draggable, 'canvas')}")
print(f"Canvas type: {type(leg._draggable.canvas)}")
print(f"Canvas is referenced in draggable: {leg._draggable.canvas is fig.canvas}")

# Now let's see what happens if we delete the canvas reference before pickling
original_canvas = leg._draggable.canvas
del leg._draggable.canvas

print("\nAfter deleting canvas reference, attempting pickle...")
pickle_data = pickle.dumps(fig)
print(f"Pickle successful, size: {len(pickle_data)} bytes")

# Now unpickle
fig2 = pickle.loads(pickle_data)
leg2 = fig2.axes[0].get_legend()
print(f"\nUnpickled legend has _draggable: {hasattr(leg2, '_draggable')}")

# Restore the canvas reference in the unpickled draggable
leg2._draggable.canvas = fig2.canvas
# Reconnect the callbacks? Wait, the callbacks are stored as cids, but they were connected with _connect_picklable
# Let's check if the callbacks still work or if we need to reconnect them
print(f"Unpickled draggable has cids: {leg2._draggable.cids}")

plt.close(fig)
plt.close(fig2)
