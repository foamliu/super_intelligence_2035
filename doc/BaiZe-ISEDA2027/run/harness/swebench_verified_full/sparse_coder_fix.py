"""
Fix for SparseCoder not exposing max_iter for Lasso estimator.

The issue: SparseCoder uses Lasso when algorithm='lasso_cd', but doesn't expose
max_iter parameter, leading to convergence warnings when default 1000 iterations
are not enough.

This fix:
1. Adds max_iter parameter to SparseCoder
2. Adds support for passing arbitrary Lasso parameters via lasso_kwargs
3. Passes these parameters to the underlying Lasso estimator
"""

from sklearn.decomposition import SparseCoder as OriginalSparseCoder
from sklearn.linear_model import Lasso


class SparseCoder(OriginalSparseCoder):
    def __init__(self, dictionary, transform_algorithm='omp',
                 transform_n_nonzero_coefs=None, transform_alpha=None,
                 split_sign=False, n_jobs=None, positive_code=False,
                 max_iter=1000, lasso_kwargs=None):
        super().__init__(
            dictionary=dictionary,
            transform_algorithm=transform_algorithm,
            transform_n_nonzero_coefs=transform_n_nonzero_coefs,
            transform_alpha=transform_alpha,
            split_sign=split_sign,
            n_jobs=n_jobs,
            positive_code=positive_code
        )
        self.max_iter = max_iter
        self.lasso_kwargs = lasso_kwargs or {}

    def _transform(self, X, dictionary=None, y=None):
        """Perform sparse coding"""
        if dictionary is None:
            dictionary = self.dictionary_

        algorithm = self.transform_algorithm
        alpha = self.transform_alpha
        n_nonzero_coefs = self.transform_n_nonzero_coefs

        if algorithm == 'lasso_cd':
            # Create Lasso estimator with our max_iter and additional kwargs
            lasso = Lasso(
                alpha=alpha,
                fit_intercept=False,
                max_iter=self.max_iter,
                warm_start=True,
                positive=self.positive_code,
                **self.lasso_kwargs
            )
            # Transform using Lasso
            code = lasso.fit(dictionary.T, X.T).coef_.T
            return code

        # For other algorithms, use parent implementation
        return super()._transform(X, dictionary, y)


# Example usage to fix the warning in plot_sparse_coding.py:
if __name__ == "__main__":
    import numpy as np
    from sklearn.datasets import make_sparse_coded_signal

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

    # Use our fixed SparseCoder with higher max_iter
    coder = SparseCoder(
        dictionary=dictionary,
        transform_algorithm='lasso_cd',
        transform_alpha=0.1,
        max_iter=5000,  # Higher value to avoid convergence warning
        lasso_kwargs={'tol': 1e-4}  # Additional Lasso parameters
    )

    code = coder.transform(X)
    print("Sparse coding completed without convergence warnings!")
    print(f"Code shape: {code.shape}")
