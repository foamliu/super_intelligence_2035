import numpy as np
from sklearn.datasets import make_regression
from sklearn.linear_model._huber import _huber_loss_and_gradient

# Test the original bug scenario: passing boolean X directly to _huber_loss_and_gradient
X, y, coef = make_regression(n_samples=200, n_features=2, noise=4.0, coef=True, random_state=0)
X_bool = X > 0

w = np.zeros(X_bool.shape[1] + 2)  # with intercept
w[-1] = 1.0

sample_weight = np.ones_like(y)
print("Testing _huber_loss_and_gradient with boolean X...")
try:
    loss, grad = _huber_loss_and_gradient(w, X_bool, y, 1.35, 0.0001, sample_weight)
    print(f"✓ Success, loss = {loss}")
except TypeError as e:
    print(f"✗ Failed with error: {e}")

print("\nTesting with float converted X...")
X_float = X_bool.astype(float)
try:
    loss, grad = _huber_loss_and_gradient(w, X_float, y, 1.35, 0.0001, sample_weight)
    print(f"✓ Success, loss = {loss}")
except TypeError as e:
    print(f"✗ Failed with error: {e}")

# Now test the fix: validate_data converts to float
from sklearn.utils.validation import validate_data
from sklearn.base import BaseEstimator

class DummyEstimator(BaseEstimator):
    pass

est = DummyEstimator()
X_validated, y_validated = validate_data(est, X_bool, y, dtype=[np.float64, np.float32])
print(f"\nAfter validate_data, X dtype is: {X_validated.dtype}")
print(f"Is float: {np.issubdtype(X_validated.dtype, np.floating)}")

try:
    loss, grad = _huber_loss_and_gradient(w, X_validated, y, 1.35, 0.0001, sample_weight)
    print(f"✓ Success with validated X, loss = {loss}")
except TypeError as e:
    print(f"✗ Failed with error: {e}")
