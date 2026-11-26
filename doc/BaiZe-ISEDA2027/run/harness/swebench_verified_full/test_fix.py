#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django'))

import django
from django.conf import settings
from django.db import models
from django.db.models import Count

# Configure minimal Django settings
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

class Article(models.Model):
    headline = models.CharField(max_length=100)
    pub_date = models.DateTimeField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True)
    
    class Meta:
        app_label = 'test'
        ordering = ['-pub_date', 'headline']  # This is the Meta.ordering that was causing the issue

# Create tables
from django.db import connection
with connection.schema_editor() as editor:
    editor.create_model(Author)
    editor.create_model(Article)

# Create test data
author1 = Author.objects.create(name="Author 1")
author2 = Author.objects.create(name="Author 2")

Article.objects.create(headline="Article 1", pub_date="2005-07-26", author=author1)
Article.objects.create(headline="Article 2", pub_date="2005-07-27", author=author1)
Article.objects.create(headline="Article 3", pub_date="2005-07-27", author=author1)
Article.objects.create(headline="Article 4", pub_date="2005-07-28", author=author2)

# Test the query that was failing
print("Running query: Article.objects.values('author').annotate(count=Count('author'))")
articles = list(Article.objects.values('author').annotate(count=Count('author')))
print(f"Result: {articles}")

# Check if the result is correct
expected = [
    {'author': author1.pk, 'count': 3},
    {'author': author2.pk, 'count': 1},
]

print(f"Expected: {expected}")

# Convert to sets for comparison
result_set = set((d['author'], d['count']) for d in articles)
expected_set = set((d['author'], d['count']) for d in expected)

if result_set == expected_set:
    print("\n✅ SUCCESS: Fix works correctly! Meta.ordering fields are not included in GROUP BY.")
    sys.exit(0)
else:
    print("\n❌ FAIL: Result doesn't match expected. Meta.ordering fields are still being added to GROUP BY.")
    # Print the generated SQL to see what's happening
    query = Article.objects.values('author').annotate(count=Count('author')).query
    print(f"\nGenerated SQL: {query}")
    sys.exit(1)
