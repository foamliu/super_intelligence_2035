"""
Test the fix logic directly without importing Django
"""
from collections import namedtuple

print("Testing the original issue:")
Range = namedtuple('Range', ['near', 'far'])
processed_values = [3, 12]

# Original code that fails
try:
    value = Range(processed_values)
    print(f"❌ Unexpected success: {value}")
except TypeError as e:
    print(f"✅ Original error reproduced: {e}")

print("\nTesting the fix using * expansion:")
try:
    value = Range(*processed_values)
    print(f"✅ Fixed using * expansion: {value}, near={value.near}, far={value.far}")
except Exception as e:
    print(f"❌ * expansion failed: {e}")

print("\nTesting the fix using _make:")
try:
    value = Range._make(processed_values)
    print(f"✅ Fixed using _make: {value}, near={value.near}, far={value.far}")
except Exception as e:
    print(f"❌ _make failed: {e}")

print("\nTesting that regular tuples still work:")
regular_tuple = (1, 2)
try:
    value = type(regular_tuple)(processed_values)
    print(f"✅ Regular tuple works: {value}")
except Exception as e:
    print(f"❌ Regular tuple failed: {e}")

print("\nTesting that lists still work:")
list_val = [1, 2]
try:
    value = type(list_val)(processed_values)
    print(f"✅ List works: {value}")
except Exception as e:
    print(f"❌ List failed: {e}")

print("\n🎉 Fix logic verified: named tuples can be correctly constructed either with * expansion or _make, while regular tuples and lists continue to work as before.")
