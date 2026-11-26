import numpy as np
from sklearn.datasets import load_iris
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
import pandas as pd

X, y = load_iris(return_X_y=True, as_frame=True)
X = X.astype(
   {
       "petal width (cm)": np.float16,
       "petal length (cm)": np.float16,
   }
)
X["cat"] = y.astype("category")

selector = SelectKBest(chi2, k=2)
# Call transform directly without set_output
X_out = selector.fit_transform(X, y)
print(f"Type of X_out: {type(X_out)}")
print(f"X_out dtypes: {X_out.dtype if hasattr(X_out, 'dtype') else [x.dtype for x in X_out.dtypes]}")

# Now with set_output
selector.set_output(transform="pandas")
X_out_df = selector.transform(X)
print(f"\nType of X_out_df: {type(X_out_df)}")
print(f"X_out_df dtypes:\n{X_out_df.dtypes}")
