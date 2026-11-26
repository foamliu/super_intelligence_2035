import numpy as np
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.ensemble import HistGradientBoostingRegressor

# Test 1: Basic fill_value with constant strategy
print("Test 1: Basic fill_value with constant strategy")
X = np.array([[1, 2, np.nan], [np.nan, 3, 4], [5, np.nan, 6]])
imputer = IterativeImputer(initial_strategy="constant", fill_value=-1, random_state=0, max_iter=1)
X_imputed = imputer.fit_transform(X)
print("Original X:")
print(X)
print("Imputed X (fill_value=-1):")
print(X_imputed)
print("Initial imputer statistics:", imputer.initial_imputer_.statistics_)
print()

# Test 2: Fill with np.nan (for decision tree compatibility)
print("Test 2: Fill with np.nan (for decision tree compatibility)")
X = np.array([[1, 2, np.nan], [np.nan, 3, 4], [5, np.nan, 6], [7, 8, 9], [10, 11, 12]])
# Use HistGradientBoostingRegressor which handles NaN values natively
imputer = IterativeImputer(
    initial_strategy="constant",
    fill_value=np.nan,
    estimator=HistGradientBoostingRegressor(random_state=0),
    random_state=0,
    max_iter=2
)
X_imputed = imputer.fit_transform(X)
print("Original X:")
print(X)
print("Imputed X (fill_value=np.nan, using HistGradientBoostingRegressor):")
print(X_imputed)
print("Initial imputer statistics:", imputer.initial_imputer_.statistics_)
print()

# Test 3: Default fill_value (should be 0 for numerical data)
print("Test 3: Default fill_value (should be 0 for numerical data)")
X = np.array([[1, 2, np.nan], [np.nan, 3, 4], [5, np.nan, 6]])
imputer = IterativeImputer(initial_strategy="constant", random_state=0, max_iter=1)
X_imputed = imputer.fit_transform(X)
print("Original X:")
print(X)
print("Imputed X (default fill_value):")
print(X_imputed)
print("Initial imputer statistics:", imputer.initial_imputer_.statistics_)
print()

# Test 4: Verify it works with full iterations
print("Test 4: Verify it works with full iterations")
X = np.array([[1, 2, np.nan], [np.nan, 3, 4], [5, np.nan, 6], [7, 8, 9]])
imputer = IterativeImputer(initial_strategy="constant", fill_value=0, random_state=0)
X_imputed = imputer.fit_transform(X)
print("Original X:")
print(X)
print("Imputed X (full iterations, initial fill_value=0):")
print(X_imputed)
