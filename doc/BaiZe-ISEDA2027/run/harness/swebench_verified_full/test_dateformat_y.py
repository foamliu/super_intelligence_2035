import datetime
import sys
sys.path.insert(0, '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/django')

import django
from django.conf import settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        TIME_ZONE='UTC',
        USE_TZ=True,
    )
    django.setup()

from django.utils.dateformat import DateFormat, format

# Test cases
test_years = [
    (1, "0001"),
    (99, "0099"),
    (999, "0999"),
    (1000, "1000"),
    (1999, "1999"),
    (2023, "2023"),
    (9999, "9999"),
]

print("Testing DateFormat.Y() zero-padding with date objects:")
print("-" * 50)

all_passed = True
for year, expected in test_years:
    d = datetime.date(year, 1, 1)
    df = DateFormat(d)
    result = df.Y()
    passed = result == expected
    all_passed = all_passed and passed
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} Year {year}: expected '{expected}', got '{result}'")

print("\nTesting DateFormat.Y() zero-padding with datetime objects:")
print("-" * 50)
for year, expected in test_years:
    d = datetime.datetime(year, 1, 1, 12, 0, 0)
    df = DateFormat(d)
    result = df.Y()
    passed = result == expected
    all_passed = all_passed and passed
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} Year {year}: expected '{expected}', got '{result}'")

print("\nTesting format() convenience function with Y specifier:")
print("-" * 50)
for year, expected in test_years:
    d = datetime.date(year, 1, 1)
    result = format(d, 'Y')
    passed = result == expected
    all_passed = all_passed and passed
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} Year {year}: expected '{expected}', got '{result}'")

print("-" * 50)
if all_passed:
    print("All tests passed!")
else:
    print("Some tests failed!")
