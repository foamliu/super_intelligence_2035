# Fix for HuberRegressor TypeError with boolean predictors

## Bug
`TypeError` when calling `HuberRegressor.fit()` with boolean X inputs:
```
TypeError: The numpy boolean negative, the `-` operator, is not supported, use the `~` operator or the logical_not function instead.
```

## Root Cause
Input validation did not convert boolean arrays to float dtype, so the `-` operator in the gradient calculation failed when applied to boolean values.

## Fix
Add `dtype=[np.float64, np.float32]` parameter to input validation in `fit()` method, which automatically converts all numeric inputs (including booleans) to float dtype.

## Files Modified
- `sklearn/linear_model/_huber.py` (or `huber.py` in older versions)

## Test Added
Verify that boolean predictors produce identical results to manually converted float predictors.

## Impact
- No breaking changes
- Works with all numeric input types
- Maintains backward compatibility
