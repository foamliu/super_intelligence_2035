# Fix for LogisticRegressionCV multinomial scoring bug

## Issue
When using `LogisticRegressionCV(multi_class='multinomial')` with probabilistic scorers like `neg_log_loss` that rely on `.predict_proba()`, the scores were being calculated using the One-vs-Rest (OvR) approach instead of the multinomial softmax approach. This happened because the internal `LogisticRegression` instance created for scoring in the `_log_reg_scoring_path` function was initialized with the default `multi_class='ovr'` instead of inheriting the `multi_class` parameter from the parent function.

## Fix
Modified line 922 (approx) in `sklearn/linear_model/logistic.py` in the `_log_reg_scoring_path` function to pass all relevant parameters to the LogisticRegression constructor:
- `multi_class=multi_class` to match the specified setting
- `penalty=penalty`, `solver=solver`, `intercept_scaling=intercept_scaling` to ensure consistency with other parameters

## Verification
After applying the fix:
1. The score returned by `_log_reg_scoring_path` when `multi_class='multinomial'` matches the expected multinomial log loss value
2. `predict_proba()` correctly uses the softmax function for multinomial classification instead of OvR normalization
3. The fix is backwards compatible, as it only passes existing parameters to the constructor

## Patch
The fix is available in `fix_logistic_regression_cv_multinomial_scoring.patch`
