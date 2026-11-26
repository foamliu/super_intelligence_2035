import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn import set_config
from sklearn.pipeline import make_union

index = pd.date_range(start="2020-01-01", end="2020-01-05", inclusive="left", freq="h")
data = pd.DataFrame(index=index, data=[10] * len(index), columns=["value"])
data["date"] = index.date


class MyTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X: pd.DataFrame, y: pd.Series | None = None, **kwargs):
        return self

    def transform(self, X: pd.DataFrame, y: pd.Series | None = None) -> pd.DataFrame:
        # Option 1: Preserve number of samples by joining aggregated values back
        agg = X["value"].groupby(X["date"]).transform("sum")
        return agg.to_frame(name="value_daily_sum")


# Test both outputs
print("Testing with default (numpy) output:")
set_config(transform_output="default")
result = make_union(MyTransformer()).fit_transform(data)
print(f"Result shape: {result.shape} (expected: ({len(data)}, 1))")
print("✅ Works!")
print("\n" + "="*50 + "\n")

print("Testing with pandas output:")
set_config(transform_output="pandas")
result = make_union(MyTransformer()).fit_transform(data)
print(f"Result shape: {result.shape} (expected: ({len(data)}, 1))")
print(f"Result index matches input index: {result.index.equals(data.index)}")
print("✅ Works!")
print("\nSample result:")
print(result.head())
