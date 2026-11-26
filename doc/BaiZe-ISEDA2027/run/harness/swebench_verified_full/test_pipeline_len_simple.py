
import sys
import os
sys.path.insert(0, os.path.abspath('./scikit_learn_repo'))

# Import directly from pipeline module to avoid build issues
from sklearn.pipeline import Pipeline

# Create a simple pipeline without needing actual estimators
pipe = Pipeline([('step1', None), ('step2', None), ('step3', None)])

print("Testing len(pipe)...")
try:
    length = len(pipe)
    print(f"len(pipe) = {length}")
    assert length == 3, f"Expected 3, got {length}"
    print("✅ len(pipe) works correctly!")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")

print("\nTesting pipe[:len(pipe)]...")
try:
    sliced = pipe[:len(pipe)]
    print(f"Sliced pipe steps: {sliced.steps}")
    assert len(sliced.steps) == 3, f"Expected 3 steps, got {len(sliced.steps)}"
    print("✅ pipe[:len(pipe)] works correctly!")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")

print("\nTesting pipe[1:3]...")
try:
    sliced = pipe[1:3]
    print(f"Sliced pipe steps: {sliced.steps}")
    assert len(sliced.steps) == 2, f"Expected 2 steps, got {len(sliced.steps)}"
    assert sliced.steps[0][0] == 'step2', f"Expected step2, got {sliced.steps[0][0]}"
    print("✅ pipe[1:3] works correctly!")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")

print("\nTesting pipe[0]...")
try:
    step = pipe[0]
    print(f"Step 0: {step}")
    assert step[0] == 'step1', f"Expected step1, got {step[0]}"
    print("✅ pipe[0] works correctly!")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")

print("\nAll tests done!")
