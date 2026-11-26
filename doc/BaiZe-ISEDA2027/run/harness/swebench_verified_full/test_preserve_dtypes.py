import numpy as np
from sklearn.datasets import load_iris
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
import pandas as pd

print("Testing preserve_dtypes feature...")
print("-" * 50)

X, y = load_iris(return_X_y=True, as_frame=True)
X = X.astype(
   {
       "petal width (cm)": np.float16,
       "petal length (cm)": np.float16,
       "sepal length (cm)": np.float32,
       "sepal width (cm)": np.float32,
   }
)
X["cat"] = y.astype("category")
X["ordinal"] = pd.cut(X["sepal length (cm)"], bins=3, labels=[0, 1, 2]).astype("category")

print("Original X dtypes:")
print(X.dtypes)
print("\n" + "-" * 50)

# Test default behavior (no preserve_dtypes)
print("Default behavior (preserve_dtypes=False):")
selector = SelectKBest(chi2, k=3)
selector.set_output(transform="pandas")
X_out = selector.fit_transform(X, y)
print(X_out.dtypes)
print("\n" + "-" * 50)

# Test with preserve_dtypes=True
print("With preserve_dtypes=True:")
selector2 = SelectKBest(chi2, k=3)
selector2.set_output(transform="pandas", preserve_dtypes=True)
X_out2 = selector2.fit_transform(X, y)
print(X_out2.dtypes)
print("\n" + "-" * 50)

# Verify values are the same
print("Values are equal:", np.allclose(X_out.to_numpy(), X_out2.to_numpy()))

# Test with ColumnTransformer to make sure it works with meta-transformers
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler

print("\n" + "=" * 50)
print("Testing with ColumnTransformer:")

ct = ColumnTransformer(
    [
        ("scale", StandardScaler(), ["sepal length (cm)", "sepal width (cm)"]),
        ("passthrough", "passthrough", ["petal length (cm)", "petal width (cm)", "cat"]),
    ],
    remainder="drop"
)

# Default behavior
ct.set_output(transform="pandas")
X_ct = ct.fit_transform(X, y)
print("ColumnTransformer default dtypes:")
print(X_ct.dtypes)
print()

# With preserve_dtypes
ct2 = ColumnTransformer(
    [
        ("scale", StandardScaler(), ["sepal length (cm)", "sepal width (cm)"]),
        ("passthrough", "passthrough", ["petal length (cm)", "petal width (cm)", "cat"]),
    ],
    remainder="drop"
)
ct2.set_output(transform="pandas", preserve_dtypes=True)
X_ct2 = ct2.fit_transform(X, y)
print("ColumnTransformer with preserve_dtypes=True dtypes:")
print(X_ct2.dtypes)
