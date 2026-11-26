import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'django'))

from django.db.models.fields import AutoField, BigAutoField, SmallAutoField

# Test custom subclasses
class MyBigAutoField(BigAutoField):
    pass

class MySmallAutoField(SmallAutoField):
    pass

class MyAutoField(AutoField):
    pass

# Test issubclass checks
print("Testing issubclass checks:")
print(f"MyBigAutoField is subclass of AutoField: {issubclass(MyBigAutoField, AutoField)}")
print(f"MySmallAutoField is subclass of AutoField: {issubclass(MySmallAutoField, AutoField)}")
print(f"MyAutoField is subclass of AutoField: {issubclass(MyAutoField, AutoField)}")
print(f"BigAutoField is subclass of AutoField: {issubclass(BigAutoField, AutoField)}")
print(f"SmallAutoField is subclass of AutoField: {issubclass(SmallAutoField, AutoField)}")

# Test the error case mentioned in the bug
try:
    # This should not raise an error anymore
    if not issubclass(MyBigAutoField, AutoField):
        raise ValueError(
            "Primary key 'example.core.models.MyBigAutoField' referred by DEFAULT_AUTO_FIELD must subclass AutoField."
        )
    print("\n✓ No error raised for MyBigAutoField")
except ValueError as e:
    print(f"\n✗ Error raised: {e}")

try:
    if not issubclass(MySmallAutoField, AutoField):
        raise ValueError(
            "Primary key 'example.core.models.MySmallAutoField' referred by DEFAULT_AUTO_FIELD must subclass AutoField."
        )
    print("✓ No error raised for MySmallAutoField")
except ValueError as e:
    print(f"✗ Error raised: {e}")
