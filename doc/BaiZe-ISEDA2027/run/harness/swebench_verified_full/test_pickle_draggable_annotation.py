import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pickle

fig = plt.figure()
ax = fig.add_subplot(111)

ax.plot([0,1,2], [1,2,3])

# Add an annotation
ann = ax.annotate('Test annotation', xy=(1, 2), xytext=(1.5, 2.5),
            arrowprops=dict(facecolor='black', shrink=0.05))
ann.set_draggable(True)

print("Attempting to pickle figure with draggable annotation...")
pickle_data = pickle.dumps(fig)
print(f"Pickle successful, size: {len(pickle_data)} bytes")

# Test unpickling
fig_unpickled = pickle.loads(pickle_data)
print("Unpickle successful")

plt.close(fig)
plt.close(fig_unpickled)
