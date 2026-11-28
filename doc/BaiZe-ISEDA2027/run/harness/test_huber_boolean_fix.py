"""Test for HuberRegressor boolean predictor fix."""
import numpy as np
from sklearn.datasets import make_regression
from sklearn.linear_model import HuberRegressor
from sklearn.utils._testing import assert_allclose


def test_huber_regressor_boolean_predictors():
    """Test that HuberRegressor.fit works with boolean predictors."""
    X, y, coef = make_regression(n_samples=200, n_features=2, noise=4.0, coef=True, random_state=0)
    X_bool = X > 0
    X_bool_as_float = np.asarray(X_bool, dtype=float)
    
    # Fit with boolean predictors
    huber_bool = HuberRegressor().fit(X_bool, y)
    # Fit with float converted predictors
    huber_float = HuberRegressor().fit(X_bool_as_float, y)
    
    # Results should be identical
    assert_allclose(huber_bool.coef_, huber_float.coef_)
    assert_allclose(huber_bool.intercept_, huber_float.intercept_)
    assert_allclose(huber_bool.scale_, huber_float.scale_)
    
    # Predict should also work
    y_pred_bool = huber_bool.predict(X_bool)
    y_pred_float = huber_float.predict(X_bool_as_float)
    assert_allclose(y_pred_bool, y_pred_float)
    
    print("✓ All tests passed! HuberRegressor works correctly with boolean predictors.")


if __name__ == "__main__":
    test_huber_regressor_boolean_predictors()
