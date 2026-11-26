import numpy as np
from sklearn.cluster import OPTICS

# Generate sample data
np.random.seed(42)
n_samples = 100
X = np.random.rand(n_samples, 2)

print("Testing OPTICS with float min_samples=0.1...")
try:
    clust = OPTICS(metric='minkowski', n_jobs=-1, min_samples=0.1)
    clust.fit(X)
    print("✅ SUCCESS! OPTICS fit completed without error.")
    print(f"   min_samples converted to: {clust.min_samples}")
    print(f"   Number of clusters found: {len(np.unique(clust.labels_))}")
except Exception as e:
    print(f"❌ FAILED with error: {type(e).__name__}: {e}")

print("\nTesting OPTICS with float min_samples=0.05...")
try:
    clust = OPTICS(metric='minkowski', n_jobs=-1, min_samples=0.05)
    clust.fit(X)
    print("✅ SUCCESS! OPTICS fit completed without error.")
    print(f"   min_samples converted to: {clust.min_samples}")
    print(f"   Number of clusters found: {len(np.unique(clust.labels_))}")
except Exception as e:
    print(f"❌ FAILED with error: {type(e).__name__}: {e}")

print("\nTesting OPTICS with integer min_samples=5 (original behavior)...")
try:
    clust = OPTICS(metric='minkowski', n_jobs=-1, min_samples=5)
    clust.fit(X)
    print("✅ SUCCESS! OPTICS fit completed without error.")
    print(f"   min_samples remains: {clust.min_samples}")
    print(f"   Number of clusters found: {len(np.unique(clust.labels_))}")
except Exception as e:
    print(f"❌ FAILED with error: {type(e).__name__}: {e}")

print("\nTesting OPTICS with float min_samples=2.7 (should round to 3)...")
try:
    clust = OPTICS(metric='minkowski', n_jobs=-1, min_samples=2.7)
    clust.fit(X)
    print("✅ SUCCESS! OPTICS fit completed without error.")
    print(f"   min_samples converted to: {clust.min_samples}")
except Exception as e:
    print(f"❌ FAILED with error: {type(e).__name__}: {e}")
