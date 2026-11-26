import numpy as np
from unittest.mock import patch

@patch(target='some.module.function', new=np.array([-5.5, 3.0]))
def test_example():
    pass

# This will trigger the error when pytest collects this test
if __name__ == "__main__":
    # Simulate what pytest does during collection
    from _pytest.compat import num_mock_patch_args
    try:
        result = num_mock_patch_args(test_example)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
