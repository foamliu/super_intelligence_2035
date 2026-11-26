import asyncio
import os
import sys
import django
from django.conf import settings
from django.db import models
from django.db.models.fields.related_descriptors import create_reverse_many_to_one_manager, create_forward_many_to_many_manager

# Configure Django settings
settings.configure(
    DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'django.contrib.auth',
    ],
)

django.setup()

# Create test models
class Author(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        app_label = 'test'

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author, related_name='books', on_delete=models.CASCADE)
    
    class Meta:
        app_label = 'test'

class Course(models.Model):
    name = models.CharField(max_length=100)
    students = models.ManyToManyField('Student', related_name='courses')
    
    class Meta:
        app_label = 'test'

class Student(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        app_label = 'test'

# Create tables
from django.db import connection
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(Author)
    schema_editor.create_model(Book)
    schema_editor.create_model(Course)
    schema_editor.create_model(Student)
    schema_editor.create_model(Course.students.through)

async def test_reverse_many_to_one_async_methods():
    print("Testing reverse many-to-one async methods...")
    
    # Create an author
    author = Author.objects.create(name="J.K. Rowling")
    
    # Test acreate
    book = await author.books.acreate(title="Harry Potter and the Philosopher's Stone")
    assert book.author == author
    assert book.title == "Harry Potter and the Philosopher's Stone"
    assert await author.books.filter(id=book.id).aexists()
    print("✓ acreate works correctly for reverse many-to-one")
    
    # Test aget_or_create - existing
    obj, created = await author.books.aget_or_create(title="Harry Potter and the Philosopher's Stone")
    assert not created
    assert obj.id == book.id
    print("✓ aget_or_create (existing) works correctly for reverse many-to-one")
    
    # Test aget_or_create - new
    obj, created = await author.books.aget_or_create(title="Harry Potter and the Chamber of Secrets")
    assert created
    assert obj.author == author
    assert await author.books.filter(id=obj.id).aexists()
    print("✓ aget_or_create (new) works correctly for reverse many-to-one")
    
    # Test aupdate_or_create - existing
    obj, created = await author.books.aupdate_or_create(
        title="Harry Potter and the Chamber of Secrets",
        defaults={"title": "Harry Potter and the Chamber of Secrets (Updated)"}
    )
    assert not created
    assert obj.title == "Harry Potter and the Chamber of Secrets (Updated)"
    print("✓ aupdate_or_create (existing) works correctly for reverse many-to-one")
    
    # Test aupdate_or_create - new
    obj, created = await author.books.aupdate_or_create(
        title="Harry Potter and the Prisoner of Azkaban",
        defaults={"title": "Harry Potter and the Prisoner of Azkaban"}
    )
    assert created
    assert obj.author == author
    assert await author.books.filter(id=obj.id).aexists()
    print("✓ aupdate_or_create (new) works correctly for reverse many-to-one")

async def test_many_to_many_async_methods():
    print("\nTesting many-to-many async methods...")
    
    # Create a course
    course = Course.objects.create(name="Potions 101")
    
    # Test acreate
    student = await course.students.acreate(name="Harry Potter")
    assert student in await course.students.aall()
    assert course in await student.courses.aall()
    print("✓ acreate works correctly for many-to-many")
    
    # Test aget_or_create - existing
    obj, created = await course.students.aget_or_create(name="Harry Potter")
    assert not created
    assert obj.id == student.id
    print("✓ aget_or_create (existing) works correctly for many-to-many")
    
    # Test aget_or_create - new
    obj, created = await course.students.aget_or_create(name="Hermione Granger")
    assert created
    assert obj in await course.students.aall()
    assert course in await obj.courses.aall()
    print("✓ aget_or_create (new) works correctly for many-to-many")
    
    # Test aupdate_or_create - existing
    obj, created = await course.students.aupdate_or_create(
        name="Hermione Granger",
        defaults={"name": "Hermione Jean Granger"}
    )
    assert not created
    assert obj.name == "Hermione Jean Granger"
    print("✓ aupdate_or_create (existing) works correctly for many-to-many")
    
    # Test aupdate_or_create - new
    obj, created = await course.students.aupdate_or_create(
        name="Ron Weasley",
        defaults={"name": "Ron Weasley"}
    )
    assert created
    assert obj in await course.students.aall()
    assert course in await obj.courses.aall()
    print("✓ aupdate_or_create (new) works correctly for many-to-many")

if __name__ == "__main__":
    asyncio.run(test_reverse_many_to_one_async_methods())
    asyncio.run(test_many_to_many_async_methods())
    print("\n✅ All tests passed!")
