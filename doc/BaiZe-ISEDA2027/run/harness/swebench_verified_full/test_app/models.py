
from django.db import models

class Publisher(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=100)
    pages = models.IntegerField()
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='books')
    
    def __str__(self):
        return self.title
