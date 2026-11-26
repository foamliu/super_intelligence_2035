"""Test cases for negative durations with negative minutes/seconds (new feature)"""
import datetime
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django'))
from django.utils.dateparse import parse_duration

# Test cases that now work after the fix
test_cases = [
    # Negative hours, negative minutes, negative seconds
    ("-1:-30:-45", datetime.timedelta(hours=-1, minutes=-30, seconds=-45)),
    ("-12:-34:-56", datetime.timedelta(hours=-12, minutes=-34, seconds=-56)),
    
    # Positive hours, negative minutes, positive seconds
    ("1:-30:45", datetime.timedelta(hours=1, minutes=-30, seconds=45)),
    
    # Positive hours, negative minutes, negative seconds
    ("2:-15:-30", datetime.timedelta(hours=2, minutes=-15, seconds=-30)),
    
    # Negative hours, positive minutes, negative seconds
    ("-3:15:-45", datetime.timedelta(hours=-3, minutes=15, seconds=-45)),
    
    # Negative minutes and seconds only
    ("-30:-45", datetime.timedelta(minutes=-30, seconds=-45)),
    
    # Negative seconds only
    ("-30", datetime.timedelta(seconds=-30)),  # already worked before
    ("--30", None),  # invalid, should return None
]

print("Testing new negative duration cases:")
all_passed = True
for input_str, expected in test_cases:
    result = parse_duration(input_str)
    if result == expected:
        print(f"✓ PASS: '{input_str}' -> {result}")
    else:
        print(f"✗ FAIL: '{input_str}' -> {result} (expected {expected})")
        all_passed = False

if all_passed:
    print("\n✅ All new test cases passed!")
else:
    print("\n❌ Some new test cases failed!")
