import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn import set_config
from sklearn.pipeline import make_union

index = pd.date_range(start="2020-01-01", end="2020-01-05", inclusive="left", freq="H")
data = pd.DataFrame(index=index, data=[10] * len(index), columns=["value"])
data["date"] = index.date


class MyTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X: pd.DataFrame, y: pd.Series | None = None, **kwargs):
        return self

    def transform(self, X: pd.DataFrame, y: pd.Series | None = None) -> pd.DataFrame:
        return X["value"].groupby(X["date"]).sum()


# This works.
print("Testing with default (numpy) output:")
set_config(transform_output="default")
result = make_union(MyTransformer()).fit_transform(data)
print(f"Result type: {type(result)}")
print(f"Result shape: {result.shape}")
print(f"Result:\n{result}")
print("\n" + "="*50 + "\n")

# This does not work.
print("Testing with pandas output:")
set_config(transform_output="pandas")
try:
    result = make_union(MyTransformer()).fit_transform(data)
    print(f"Result type: {type(result)}")
    print(f"Result shape: {result.shape}")
    print(f"Result:\n{result}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
