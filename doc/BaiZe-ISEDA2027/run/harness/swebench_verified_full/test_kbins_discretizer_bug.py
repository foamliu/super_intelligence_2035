import numpy as np
from sklearn.preprocessing import KBinsDiscretizer

X = np.array([0, 0.5, 2, 3, 9, 10]).reshape(-1, 1)

# with 5 bins
est = KBinsDiscretizer(n_bins=5, strategy='kmeans', encode='ordinal')
Xt = est.fit_transform(X)
print(Xt)
