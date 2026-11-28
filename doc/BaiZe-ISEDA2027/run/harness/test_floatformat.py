import sys
sys.path.insert(0, '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/django')
from decimal import Decimal
from django.template.defaultfilters import floatformat

print("Testing floatformat('0.00', 0)...")
try:
    result = floatformat('0.00', 0)
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting floatformat(Decimal('0.00'), 0)...")
try:
    result = floatformat(Decimal('0.00'), 0)
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Let's debug the steps for Decimal('0.00')
d = Decimal('0.00')
print(f"\nDebugging for d = {d!r}")
print(f"d.as_tuple(): {d.as_tuple()}")
m = int(d) - d
print(f"m = {m!r}")
print(f"not m: {not m}")
p = 0
print(f"p = {p}")
print(f"not m and p <=0: {not m and p <=0}")
