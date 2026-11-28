from django.db import models

f = models.CharField(max_length=200)
d = {f: 1}
print(f"Hash before assignment to model: {hash(f)}")

class Book(models.Model):
    title = f

print(f"Hash after assignment to model: {hash(f)}")
print(f"Is f in d? {f in d}")
assert f in d, "Field not found in dict after assignment to model!"
print("Test passed!")
