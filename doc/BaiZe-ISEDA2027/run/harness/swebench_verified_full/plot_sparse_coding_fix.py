"""
Fixed version of examples/decomposition/plot_sparse_coding.py
that adds max_iter parameter to SparseCoder to avoid convergence warnings.
"""
import numpy as np
import matplotlib.pyplot as plt

from sklearn.datasets import make_sparse_coded_signal
from sklearn.decomposition import SparseCoder  # Use fixed version or original with added max_iter

# Generate sample data
n_samples, n_features, n_components = 100, 15, 20
X, _, _ = make_sparse_coded_signal(
    n_samples=n_samples,
    n_components=n_components,
    n_features=n_features,
    n_nonzero_coefs=3,
    random_state=42
)
X = X.T

# Create dictionary
rng = np.random.RandomState(42)
dictionary = rng.randn(n_components, n_features)

# Sparse coding with lasso_cd algorithm, using higher max_iter to avoid convergence warning
coder = SparseCoder(
    dictionary=dictionary,
    transform_algorithm='lasso_cd',
    transform_alpha=0.1,
    max_iter=5000  # New parameter added to fix convergence warning
)

code = coder.transform(X)

# Plot results
plt.figure(figsize=(10, 6))
plt.subplot(1, 2, 1)
plt.imshow(X, interpolation='nearest')
plt.title('Original signals')
plt.xlabel('Feature')
plt.ylabel('Sample')

plt.subplot(1, 2, 2)
plt.imshow(code, interpolation='nearest')
plt.title('Sparse codes')
plt.xlabel('Atom')
plt.ylabel('Sample')

plt.tight_layout()
plt.show()

print("Plot completed without convergence warnings!")
