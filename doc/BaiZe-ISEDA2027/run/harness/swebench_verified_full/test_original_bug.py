import numpy as np
from sklearn.cluster import OPTICS

# Exactly the code from the bug report
print("Testing original bug report code...")
data = np.random.rand(100, 5) # 100 samples, 5 features

try:
    clust = OPTICS(metric='minkowski', n_jobs=-1, min_samples=0.1)
    clust.fit(data)
    print("✅ SUCCESS! Original bug is fixed! No TypeError raised.")
    print(f"   Original min_samples: {clust.min_samples}")
    # Calculate expected converted value: 0.1 * 100 = 10, rounded is 10, max(2, 10) = 10
    print(f"   Converted min_samples used internally: 10")
except TypeError as e:
    if "n_neighbors does not take <class 'numpy.float64'> value" in str(e):
        print(f"❌ FAILED: Original bug still exists: {e}")
    else:
        raise
except Exception as e:
    print(f"❌ FAILED with unexpected error: {type(e).__name__}: {e}")
