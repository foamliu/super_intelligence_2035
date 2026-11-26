from django.db import models

# Test the exact example from the bug report
f = models.CharField(max_length=200)
d = {f: 1}

class Book(models.Model):
    title = f

assert f in d, "Field not found in dict after assignment to model"
print("Test passed! Field is correctly found in dict after assignment to model.")

# Also test that equality still works correctly
f2 = models.CharField(max_length=200)
assert f != f2, "Different fields should not be equal"

# Test that two fields from different models with same creation_counter are not equal
# (though they will have same hash, which is okay)
g = models.CharField(max_length=100)
d2 = {g: 2}
class Author(models.Model):
    name = g

assert g in d2, "Second field not found in dict"
assert f not in d2, "First field should not be in second dict"
assert g not in d, "Second field should not be in first dict"

print("All equality tests passed!")
