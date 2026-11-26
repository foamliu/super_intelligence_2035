import numpy as np
from sklearn.datasets import make_regression
from sklearn.linear_model import HuberRegressor

# Random data
X, y, coef = make_regression(n_samples=200, n_features=2, noise=4.0, coef=True, random_state=0)
X_bool = X > 0
X_bool_as_float = np.asarray(X_bool, dtype=float)

print("Testing HuberRegressor with float X...")
# Works
huber = HuberRegressor().fit(X, y)
print("✓ Success with float X")

print("\nTesting HuberRegressor with bool X...")
# Previously failed, should now work
huber = HuberRegressor().fit(X_bool, y)
print("✓ Success with bool X")

print("\nTesting HuberRegressor with bool converted to float X...")
# Also works
huber = HuberRegressor().fit(X_bool_as_float, y)
print("✓ Success with bool as float X")

print("\nAll tests passed!")
