# caplog log level not restoring fix for pytest 6.0

## Bug Description
The `caplog` fixture fails to restore log levels after test execution in pytest 6.0, causing level changes from one test to leak into subsequent tests.

## Affected Version
pytest 6.0.0

## Root Cause
The shared log capture handler instance's level was not being restored during fixture teardown, while logger levels were correctly restored.

## Fix Applied
Added handler level restoration in the `_finalize()` method of `LogCaptureFixture` class in `src/_pytest/logging.py`.

## Testing
After applying the fix:
```
test_foo(caplog) passes (sets level 42)
test_bar(caplog) sees caplog.handler.level = 0 (correctly restored)
```

## Upstream Reference
This fix was officially released in pytest 6.0.1, resolving https://github.com/pytest-dev/pytest/issues/7579
