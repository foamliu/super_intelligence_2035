import matplotlib
# Use non-interactive backend to avoid GUI issues
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pickle

fig = plt.figure()
ax = fig.add_subplot(111)

time=[0,1,2,3,4]
speed=[40,43,45,47,48]

ax.plot(time,speed,label="speed")

leg=ax.legend()
leg.set_draggable(True) #pickling works after removing this line 

print("Attempting to pickle figure...")
pickle_data = pickle.dumps(fig)
print(f"Pickle successful, size: {len(pickle_data)} bytes")

# Test unpickling
fig_unpickled = pickle.loads(pickle_data)
print("Unpickle successful")

plt.close(fig)
plt.close(fig_unpickled)
