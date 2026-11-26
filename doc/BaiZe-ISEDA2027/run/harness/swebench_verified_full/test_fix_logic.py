import numpy as np

# Simulate the fix logic
def get_first_threshold(max_score):
    if max_score < 1:
        return 1.0
    elif max_score == 1:
        return np.nextafter(1.0, np.inf)
    else:
        return max_score + 1

# Test cases
test_cases = [
    (0.8, 1.0, "Probability max < 1"),
    (0.999999, 1.0, "Probability max close to 1"),
    (1.0, np.nextafter(1.0, np.inf), "Probability max exactly 1"),
    (2.0, 3.0, "Decision function max >1"),
    (100.5, 101.5, "Large decision function value"),
]

print("Testing first threshold logic:")
print("-" * 50)
all_passed = True
for max_score, expected, desc in test_cases:
    result = get_first_threshold(max_score)
    passed = np.isclose(result, expected) if not isinstance(expected, float) or not np.isinf(expected) else result == expected
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status} {desc}: max_score={max_score} → result={result} (expected={expected})")
    if not passed:
        all_passed = False

print("-" * 50)
if all_passed:
    print("All logic tests passed! The fix works as expected.")
else:
    print("Some tests failed.")

# Also test the example from the user's issue
print("\n\nUser's example test:")
rng = np.random.RandomState(42)
y_true = rng.randint(0, 2, size=10)
y_score = rng.rand(10)
max_score = y_score.max()
first_threshold = get_first_threshold(max_score)
print(f"y_score max: {max_score}")
print(f"First threshold: {first_threshold}")
print(f"Threshold <=1: {first_threshold <= 1.0}")
print(f"Threshold > max_score: {first_threshold > max_score}")
print("This ensures no samples are predicted above the first threshold (fpr=0, tpr=0)")
