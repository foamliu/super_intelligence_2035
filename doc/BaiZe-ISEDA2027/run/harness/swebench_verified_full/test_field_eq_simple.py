import sys
sys.path.insert(0, './django')

from django.db.models.fields import Field, IntegerField

# Create mock model classes
class MockModelA:
    _meta = type('Meta', (), {'app_label': 'test', 'model_name': 'a'})()

class MockModelB:
    _meta = type('Meta', (), {'app_label': 'test', 'model_name': 'b'})()

# Create a field
field = IntegerField()

# Simulate what happens when inheriting from abstract class:
# Create two copies of the field with same creation counter
field1 = IntegerField()
field1.creation_counter = field.creation_counter
field1.model = MockModelA

field2 = IntegerField()
field2.creation_counter = field.creation_counter
field2.model = MockModelB

print(f"Field 1 creation counter: {field1.creation_counter}")
print(f"Field 2 creation counter: {field2.creation_counter}")
print(f"Field 1 model: {field1.model}")
print(f"Field 2 model: {field2.model}")
print(f"Are fields equal? {field1 == field2}")
print(f"Length of set containing both fields: {len({field1, field2})}")

# Test that same model fields are equal
field1_copy = IntegerField()
field1_copy.creation_counter = field.creation_counter
field1_copy.model = MockModelA
print(f"\nField 1 vs same field with same model: {field1 == field1_copy}")
print(f"Length of set containing same field twice: {len({field1, field1_copy})}")

# Test ordering
print(f"\nfield1 < field2? {field1 < field2}")
print(f"field2 < field1? {field2 < field1}")
