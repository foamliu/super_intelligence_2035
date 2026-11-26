import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn import set_config
from sklearn.pipeline import make_union, make_pipeline
from sklearn.compose import ColumnTransformer

index = pd.date_range(start="2020-01-01", end="2020-01-05", inclusive="left", freq="h")
data = pd.DataFrame(index=index, data=[10] * len(index), columns=["value"])
data["date"] = index.date
data["value2"] = data["value"] * 2


class SumByDate(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        # Return aggregated DataFrame with date index (4 rows)
        return X.groupby("date")["value"].sum().to_frame(name="sum_value")

class MeanByDate(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        # Return aggregated DataFrame with date index (4 rows)
        return X.groupby("date")["value2"].mean().to_frame(name="mean_value2")


print("Scenario: Multiple transformers returning aggregated 4-row results")
print("="*70)

# Workaround 1: Don't use global pandas output, convert manually
print("\nWorkaround 1: Use default output, manually convert to DataFrame")
set_config(transform_output="default")
union = make_union(SumByDate(), MeanByDate())
result_np = union.fit_transform(data)
# Get feature names
feature_names = union.get_feature_names_out()
# Get index from one of the transformers (they both have same index)
result_index = SumByDate().fit_transform(data).index
# Create DataFrame manually
result_df = pd.DataFrame(result_np, columns=feature_names, index=result_index)
print(f"Result shape: {result_df.shape}")
print(f"Result:\n{result_df}")
print("✅ Works!")

# Workaround 2: Use a custom transformer that combines results and preserves index
print("\n" + "="*70 + "\n")
print("Workaround 2: Custom combiner transformer that preserves aggregated index")

class AggregationUnion(BaseEstimator, TransformerMixin):
    def __init__(self, transformers):
        self.transformers = transformers
    
    def fit(self, X, y=None):
        for name, trans in self.transformers:
            trans.fit(X, y)
        return self
    
    def transform(self, X):
        results = []
        index = None
        for name, trans in self.transformers:
            res = trans.transform(X)
            if index is None:
                index = res.index
            else:
                assert index.equals(res.index), "All transformers must return same index"
            # Rename columns to avoid conflicts
            res = res.add_prefix(f"{name}__")
            results.append(res)
        return pd.concat(results, axis=1)

union = AggregationUnion([
    ("sum", SumByDate()),
    ("mean", MeanByDate())
])
result = union.fit_transform(data)
print(f"Result shape: {result.shape}")
print(f"Result:\n{result}")
print("✅ Works!")
