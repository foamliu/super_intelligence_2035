from django.db.models import Value

# Test the original issue
x = Value('test')
y = x._resolve_output_field()
print(f"CharField validators: {y.validators}")
print(f"Number of validators: {len(y.validators)}")

# Test that clean doesn't throw TypeError anymore
try:
    result = y.clean('1', model_instance=None)
    print(f"Clean succeeded, result: {result}")
except TypeError as e:
    print(f"Clean failed with TypeError: {e}")

# Test that CharField with max_length still has the validator
from django.db.models import CharField as ModelCharField
field_with_max_length = ModelCharField(max_length=100)
print(f"\nCharField with max_length=100 validators: {field_with_max_length.validators}")
print(f"Number of validators: {len(field_with_max_length.validators)}")
