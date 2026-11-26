import datetime
import sys
sys.path.insert(0, '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/django')
from utils.dateformat import DateFormat

# Test cases
test_years = [
    (1, "0001"),
    (99, "0099"),
    (999, "0999"),
    (1000, "1000"),
    (1999, "1999"),
    (2023, "2023"),
    (9999, "9999"),
    (10000, "10000"),
]

print("Testing DateFormat.Y() zero-padding:")
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

print("-" * 50)
if all_passed:
    print("All tests passed!")
else:
    print("Some tests failed!")
