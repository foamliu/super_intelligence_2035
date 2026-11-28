from matplotlib import pyplot
import numpy as np

np.random.seed(42)

X, Y = np.random.multivariate_normal([0.0, 0.0], [[1.0, 0.1], [0.1, 1.0]], size=250).T
Z = np.ones_like(X)

extent = [-3., 3., -3., 3.]
gridsize = (7, 7)

print("Test 1: No C, mincnt=1")
fig, ax = pyplot.subplots(1, 1)
hb1 = ax.hexbin(
    X, Y,
    mincnt=1,
    extent=extent,
    gridsize=gridsize,
    linewidth=0.0,
    cmap='Blues',
)
counts1 = hb1.get_array()
print(f"Number of bins shown: {len(counts1)}")
pyplot.close(fig)

print("\nTest 2: C=Z, mincnt=1")
fig, ax = pyplot.subplots(1, 1)
hb2 = ax.hexbin(
    X, Y,
    C=Z,
    reduce_C_function=np.sum,
    mincnt=1,
    extent=extent,
    gridsize=gridsize,
    linewidth=0.0,
    cmap='Blues',
)
counts2 = hb2.get_array()
print(f"Number of bins shown: {len(counts2)}")
pyplot.close(fig)

print("\nTest 3: C=Z, mincnt=0")
fig, ax = pyplot.subplots(1, 1)
hb3 = ax.hexbin(
    X, Y,
    C=Z,
    reduce_C_function=np.sum,
    mincnt=0,
    extent=extent,
    gridsize=gridsize,
    linewidth=0.0,
    cmap='Blues',
)
counts3 = hb3.get_array()
print(f"Number of bins shown: {len(counts3)}")
pyplot.close(fig)

print(f"\nExpected: Test1 count == Test2 count == Test3 count")
print(f"Actual: Test1={len(counts1)}, Test2={len(counts2)}, Test3={len(counts3)}")
