# Bugfix: unittest.TestCase.tearDown executed on skipped tests when running --pdb

## Affected Versions
pytest >= 5.4.2

## Root Cause
When the `--pdb` flag is enabled, the pytest unittest plugin postpones executing the test case's `tearDown` method to the pytest item teardown phase, to keep instance variables available for debugging. However, pytest runs this teardown phase for all test items, including skipped tests, while the standard unittest framework never calls `tearDown` for skipped tests. This mismatch causes `tearDown` to run for skipped tests when `--pdb` is enabled.

## Fix
Add a check in the `TestCaseFunction.teardown` method to skip executing the postponed tearDown if the test was marked as skipped:
- Uses the existing `skipped_by_mark_key` flag that is set when a unittest skip is encountered
- Preserves the debugging functionality for non-skipped failing tests
- Restores behavior matching pytest <= 5.4.1

## Test Case
```python
import unittest

class MyTestCase(unittest.TestCase):
    def setUp(self):
        xxx
    @unittest.skip("hello")
    def test_one(self):
        pass
    def tearDown(self):
        xxx
```
Running `pytest --pdb test_repro.py` should skip the test without triggering the `NameError` in `tearDown`.
