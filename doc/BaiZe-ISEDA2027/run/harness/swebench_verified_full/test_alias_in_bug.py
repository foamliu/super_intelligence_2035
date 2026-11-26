
import django
from django.conf import settings
import os
import sys

# Setup Django
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
        'test_app',
    ]
)

django.setup()

from test_app.models import Book, Publisher
from django.db.models import Value

# Create test data
p1 = Publisher.objects.create(name='Apress')
p2 = Publisher.objects.create(name='Sams')
p3 = Publisher.objects.create(name='Prentice Hall')
p4 = Publisher.objects.create(name='Morgan Kaufmann')
p5 = Publisher.objects.create(name='Other')

Book.objects.create(title='Book 1', pages=500, publisher=p1)
Book.objects.create(title='Book 2', pages=600, publisher=p2)
Book.objects.create(title='Book 3', pages=450, publisher=p3)
Book.objects.create(title='Book 4', pages=700, publisher=p4)
Book.objects.create(title='Book 5', pages=300, publisher=p5)

# Test case from the bug report
def test_annotation_and_alias_filter_in_subquery():
    long_books_qs = (
        Book.objects.filter(
            pages__gt=400,
        )
        .annotate(book_annotate=Value(1))
        .alias(book_alias=Value(1))
    )
    print("Long books query SQL:", long_books_qs.query)
    publisher_books_qs = (
        Publisher.objects.filter(
            book__in=long_books_qs
        )
        .values("name")
    )
    print("\nPublisher query SQL:", publisher_books_qs.query)
    try:
        result = list(publisher_books_qs)
        print("\nResult:", result)
        expected = [
            {'name': 'Apress'},
            {'name': 'Sams'},
            {'name': 'Prentice Hall'},
            {'name': 'Morgan Kaufmann'}
        ]
        print("Expected:", expected)
        print("Test passed:", sorted(result, key=lambda x: x['name']) == sorted(expected, key=lambda x: x['name']))
    except Exception as e:
        print(f"\nError: {type(e).__name__}: {e}")

if __name__ == "__main__":
    # Make migrations and migrate
    from django.core.management import execute_from_command_line
    execute_from_command_line([sys.argv[0], 'makemigrations', 'test_app'])
    execute_from_command_line([sys.argv[0], 'migrate'])
    test_annotation_and_alias_filter_in_subquery()
