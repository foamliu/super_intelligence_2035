import numpy as np
import sys
sys.path.insert(0, '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/scikit_learn_repo')

from sklearn.metrics import roc_curve

# Test 1: Probability estimates between 0 and 1
print("Test 1: Probability estimates between 0 and 1")
rng = np.random.RandomState(42)
y_true = rng.randint(0, 2, size=10)
y_score = rng.rand(10)
_, _, thresholds = roc_curve(y_true, y_score)
print(f"Thresholds: {thresholds}")
print(f"All thresholds >=0: {np.all(thresholds >= 0)}")
print(f"All thresholds <=1: {np.all(thresholds <= 1)}")
assert np.logical_and(thresholds >= 0, thresholds <= 1).all(), "Thresholds out of range for probabilities"
print("✓ Test 1 passed\n")

# Test 2: Max score exactly 1.0
print("Test 2: Max score exactly 1.0")
y_true = [0, 1, 0, 1]
y_score = [0.2, 1.0, 0.5, 0.9]
_, _, thresholds = roc_curve(y_true, y_score)
print(f"Thresholds: {thresholds}")
print(f"First threshold >1: {thresholds[0] > 1.0}")
print(f"Remaining thresholds <=1: {np.all(thresholds[1:] <= 1.0)}")
assert thresholds[0] > 1.0
assert np.all(thresholds[1:] <= 1.0)
print("✓ Test 2 passed\n")

# Test 3: Decision function values >1
print("Test 3: Decision function values >1")
y_true = [0, 1, 0, 1]
y_score = [0.5, 2.0, 1.5, 3.0]
_, _, thresholds = roc_curve(y_true, y_score)
print(f"Thresholds: {thresholds}")
print(f"First threshold = max +1 = 4.0: {thresholds[0] == 4.0}")
assert thresholds[0] == 4.0
print("✓ Test 3 passed\n")

# Test 4: Check that ROC curve still works correctly (fpr, tpr values)
print("Test 4: ROC curve correctness")
y_true = [1, 1, 2, 2]
scores = [0.1, 0.4, 0.35, 0.8]
fpr, tpr, thresholds = roc_curve(y_true, scores, pos_label=2)
print(f"FPR: {fpr}")
print(f"TPR: {tpr}")
print(f"Thresholds: {thresholds}")
expected_fpr = [0., 0., 0.5, 0.5, 1.]
expected_tpr = [0., 0.5, 0.5, 1., 1.]
expected_thresholds = [1.0, 0.8, 0.4, 0.35, 0.1]
assert np.allclose(fpr, expected_fpr)
assert np.allclose(tpr, expected_tpr)
assert np.allclose(thresholds, expected_thresholds)
print("✓ Test 4 passed\n")

print("All tests passed! 🎉")
