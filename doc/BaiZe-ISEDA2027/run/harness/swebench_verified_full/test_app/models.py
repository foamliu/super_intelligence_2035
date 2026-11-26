
from django.db import models

class MyBigAutoField(models.BigAutoField):
    pass

class MyModel(models.Model):
    name = models.CharField(max_length=100)
