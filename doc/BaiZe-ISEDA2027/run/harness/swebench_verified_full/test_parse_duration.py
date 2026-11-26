import datetime
from django.utils.dateparse import parse_duration

# Test cases for negative durations
test_cases = [
    # Positive cases (should still work)
    ("1:00:00", datetime.timedelta(hours=1)),
    ("01:00:00", datetime.timedelta(hours=1)),
    ("1:30:45", datetime.timedelta(hours=1, minutes=30, seconds=45)),
    ("2 days 1:30:45", datetime.timedelta(days=2, hours=1, minutes=30, seconds=45)),
    ("1.5", datetime.timedelta(seconds=1.5)),
    ("0:00:00.000001", datetime.timedelta(microseconds=1)),
    
    # Negative cases that should now work
    ("-1:00:00", datetime.timedelta(hours=-1)),
    ("-01:00:00", datetime.timedelta(hours=-1)),
    ("-1:30:45", datetime.timedelta(hours=-1, minutes=-30, seconds=-45)),
    ("-2 days 1:30:45", datetime.timedelta(days=-2, hours=1, minutes=30, seconds=45)),
    ("2 days -1:30:45", datetime.timedelta(days=2, hours=-1, minutes=-30, seconds=-45)),
    ("-1.5", datetime.timedelta(seconds=-1.5)),
    ("-0:00:00.000001", datetime.timedelta(microseconds=-1)),
]

all_passed = True
for input_str, expected in test_cases:
    result = parse_duration(input_str)
    if result == expected:
        print(f"✓ PASS: '{input_str}' -> {result}")
    else:
        print(f"✗ FAIL: '{input_str}' -> {result} (expected {expected})")
        all_passed = False

if all_passed:
    print("\n✅ All tests passed!")
else:
    print("\n❌ Some tests failed!")
