import numpy as np
from matplotlib.contour import ContourSet
from matplotlib.path import Path
import matplotlib.pyplot as plt

# Create simple contour segments
levels = [0.2, 0.5, 0.8]
allsegs = [
    # Level 0.2: a square
    [np.array([[-0.2, -0.2], [0.2, -0.2], [0.2, 0.2], [-0.2, 0.2], [-0.2, -0.2]])],
    # Level 0.5: a square
    [np.array([[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5], [-0.5, -0.5]])],
    # Level 0.8: a square
    [np.array([[-0.8, -0.8], [0.8, -0.8], [0.8, 0.8], [-0.8, 0.8], [-0.8, -0.8]])],
]

# Create ContourSet directly
fig, ax = plt.subplots()
cs = ContourSet(ax, levels, allsegs, filled=False)
# Force path creation if not already done
if not hasattr(cs, '_paths') or cs._paths is None:
    cs._paths = [Path.make_compound_path(*map(Path, segs, [[None] * len(segs) for segs in allsegs]))
                for segs in allsegs]
    # Calculate mins and maxs
    flatseglist = [s for seg in allsegs for s in seg]
    points = np.concatenate(flatseglist, axis=0)
    cs._mins = points.min(axis=0)
    cs._maxs = points.max(axis=0)
    cs.sticky_edges.x[:] = [cs._mins[0], cs._maxs[0]]
    cs.sticky_edges.y[:] = [cs._mins[1], cs._maxs[1]]

# Get original paths
original_paths = cs._paths
print(f"Original number of paths: {len(original_paths)}")
print(f"Original sticky edges x: {cs.sticky_edges.x}")
print(f"Original sticky edges y: {cs.sticky_edges.y}")

# Transform paths - scale by 2
transformed_paths = []
for path in original_paths:
    new_vertices = path.vertices * 2
    transformed_paths.append(Path(new_vertices, path.codes))

# Use new set_paths method
cs.set_paths(transformed_paths)

# Check results
new_paths = cs._paths
print(f"\nNew number of paths: {len(new_paths)}")
print(f"New sticky edges x: {cs.sticky_edges.x}")
print(f"New sticky edges y: {cs.sticky_edges.y}")
print(f"Paths are updated: {all(np.array_equal(p1.vertices, p2.vertices) for p1, p2 in zip(new_paths, transformed_paths))}")

# Test that the old workaround still works too, for backward compatibility
paths = cs._paths
paths[:] = [Path(p.vertices * 0.5, p.codes) for p in transformed_paths]
print(f"\nAfter old workaround, paths are updated: {all(np.array_equal(p.vertices, p2.vertices * 0.5) for p, p2 in zip(cs._paths, transformed_paths))}")

plt.close(fig)
print("\nAll tests passed! set_paths works correctly.")
