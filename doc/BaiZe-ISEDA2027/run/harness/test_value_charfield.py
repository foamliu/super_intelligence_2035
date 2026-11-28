from django.db.models import Value

# Test the issue mentioned
x = Value('test')
y = x._resolve_output_field()
print(f"CharField max_length: {y.max_length}")
print(f"Validators: {y.validators}")

# Test that clean doesn't throw TypeError
try:
    result = y.clean('1', model_instance=None)
    print(f"Clean succeeded, result: {result}")
except TypeError as e:
    print(f"Clean failed with TypeError: {e}")
