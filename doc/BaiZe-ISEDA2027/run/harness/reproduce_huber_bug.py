import numpy as np
import sklearn
print(f"scikit-learn version: {sklearn.__version__}")
from sklearn.datasets import make_regression
from sklearn.linear_model import HuberRegressor

# Random data
X, y, coef = make_regression(n_samples=200, n_features=2, noise=4.0, coef=True, random_state=0)
X_bool = X > 0
X_bool_as_float = np.asarray(X_bool, dtype=float)

print("Testing with float X...")
huber = HuberRegressor().fit(X, y)
print("✓ Success")

print("\nTesting with boolean X...")
try:
    huber = HuberRegressor().fit(X_bool, y)
    print("✓ Success")
except TypeError as e:
    print(f"✗ Failed with error: {e}")

print("\nTesting with boolean converted to float X...")
huber = HuberRegressor().fit(X_bool_as_float, y)
print("✓ Success")
