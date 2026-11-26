import datetime
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django'))
from django.utils.dateparse import parse_duration

print("Testing original issue cases (negative minutes/seconds):")

# These should now match (they didn't before)
test_cases = [
    # Cases that didn't match before the fix
    ("1:-30:45", datetime.timedelta(hours=1, minutes=-30, seconds=45)),
    ("-1:-30:-45", datetime.timedelta(hours=-1, minutes=-30, seconds=-45)),
    ("2 days -1:-30:-45", datetime.timedelta(days=2, hours=-1, minutes=-30, seconds=-45)),
    ("-2 days 1:-30:45", datetime.timedelta(days=-2, hours=1, minutes=-30, seconds=45)),
    ("-0:-0:-1", datetime.timedelta(seconds=-1)),
]

all_passed = True
for input_str, expected in test_cases:
    result = parse_duration(input_str)
    if result == expected:
        print(f"✓ PASS: '{input_str}' -> {result}")
    else:
        print(f"✗ FAIL: '{input_str}' -> {result} (expected {expected})")
        all_passed = False

# Also test that normal cases still work
print("\nTesting normal positive cases still work:")
normal_cases = [
    ("1:00:00", datetime.timedelta(hours=1)),
    ("01:00:00", datetime.timedelta(hours=1)),
    ("1:30:45", datetime.timedelta(hours=1, minutes=30, seconds=45)),
    ("2 days 1:30:45", datetime.timedelta(days=2, hours=1, minutes=30, seconds=45)),
    ("1.5", datetime.timedelta(seconds=1.5)),
    ("0:00:00.000001", datetime.timedelta(microseconds=1)),
]

for input_str, expected in normal_cases:
    result = parse_duration(input_str)
    if result == expected:
        print(f"✓ PASS: '{input_str}' -> {result}")
    else:
        print(f"✗ FAIL: '{input_str}' -> {result} (expected {expected})")
        all_passed = False

if all_passed:
    print("\n✅ All tests passed! The fix is working correctly.")
    print("\nThe issue is resolved: the regex now matches durations with negative minutes or seconds,")
    print("which was not possible before the fix.")
else:
    print("\n❌ Some tests failed!")
