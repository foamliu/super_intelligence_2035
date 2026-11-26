# Fix Summary: HistGradientBoostingClassifier string target early stopping error

## Problem
HistGradientBoostingClassifier threw a TypeError when using string targets with early stopping enabled. The error occurred because the scorer received integer-encoded `y_true` values but string `y_pred` values from the predict() method, leading to a type mismatch when computing accuracy.

## Root Cause
- During training, the target labels are encoded to integers (0, 1, ...) using LabelEncoder in the `_encode_y` method
- The predict() method converts predicted integers back to the original string class labels using `self.classes_`
- In the `_check_early_stopping_scorer` method, the integer-encoded y values were passed directly to the scorer without conversion, causing a mismatch with the string predictions

## Fix Applied
Modified the `_check_early_stopping_scorer` method in `/scikit_learn_repo/sklearn/ensemble/_hist_gradient_boosting/gradient_boosting.py`:
1. Added a check for the existence of `self.classes_` (present for classifiers)
2. Convert integer y values back to original class labels using `self.classes_[y.astype(int)]` before passing to the scorer
3. Applied conversion to both training and validation y values

## Code Changes
```diff
def _check_early_stopping_scorer(self, X_binned_small_train, y_small_train,
                                 X_binned_val, y_val):
    """Check if fitting should be early-stopped based on scorer.

    Scores are computed on validation data or on training data.
    """
+   if hasattr(self, 'classes_'):
+       y_small_train = self.classes_[y_small_train.astype(int)]
    self.train_score_.append(
        self.scorer_(self, X_binned_small_train, y_small_train)
    )

    if self._use_validation_data:
+       if hasattr(self, 'classes_'):
+           y_val = self.classes_[y_val.astype(int)]
        self.validation_score_.append(
            self.scorer_(self, X_binned_val, y_val)
        )
        return self._should_stop(self.validation_score_)
    else:
        return self._should_stop(self.train_score_)
```

## Verification
The fix matches exactly the approach suggested in the issue report. It ensures that both `y_true` and `y_pred` passed to the scorer are of the same type (original class labels), eliminating the type mismatch error. This maintains consistency with how predictions are returned to users.
