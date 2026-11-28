
import numpy as np
from sklearn.metrics.cluster import fowlkes_mallows_score

# Create large labels to trigger the overflow
n_samples = 1000000
n_clusters = 10000

# Generate random labels
labels_true = np.random.randint(0, n_clusters, size=n_samples)
labels_pred = np.random.randint(0, n_clusters, size=n_samples)

# This should trigger the RuntimeWarning and return nan
print("Calculating Fowlkes-Mallows score...")
score = fowlkes_mallows_score(labels_true, labels_pred)
print(f"Score: {score}")
