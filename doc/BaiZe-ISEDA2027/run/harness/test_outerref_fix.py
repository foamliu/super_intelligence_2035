from django.db import models
from django.db.models import Exists, OuterRef, Q
from django.test import TestCase

class Number(models.Model):
    num = models.IntegerField()

    class Meta:
        app_label = 'test'

class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'test'

class Tag(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        app_label = 'test'

class Item(models.Model):
    name = models.CharField(max_length=100)
    tags = models.ManyToManyField(Tag)

    class Meta:
        app_label = 'test'

class TestExistsExclude(TestCase):
    def test_exists_exclude(self):
        # Create test data
        cat1 = Category.objects.create(name='Cat1')
        cat2 = Category.objects.create(name='Cat2')
        tag1 = Tag.objects.create(name='Tag1', category=cat1)
        tag2 = Tag.objects.create(name='Tag2', category=cat2)
        item1 = Item.objects.create(name='Item1')
        item1.tags.add(tag1)
        item2 = Item.objects.create(name='Item2')
        item2.tags.add(tag2)
        num1 = Number.objects.create(num=cat1.pk)
        num2 = Number.objects.create(num=cat2.pk)

        # filter() - should work
        qs = Number.objects.annotate(
            foo=Exists(
                Item.objects.filter(tags__category_id=OuterRef('pk'))
            )
        ).filter(foo=True)
        self.assertEqual(qs.count(), 2)
        
        # exclude() - was crashing before fix
        qs = Number.objects.annotate(
            foo=Exists(
                Item.objects.exclude(tags__category_id=OuterRef('pk'))
            )
        ).filter(foo=True)
        self.assertEqual(qs.count(), 2)
        
        # filter(~Q()) - was crashing before fix
        qs = Number.objects.annotate(
            foo=Exists(
                Item.objects.filter(~Q(tags__category_id=OuterRef('pk')))
            )
        ).filter(foo=True)
        self.assertEqual(qs.count(), 2)

if __name__ == '__main__':
    import django
    from django.conf import settings
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=['test'],
    )
    django.setup()
    from django.db import connection
    with connection.schema_editor() as editor:
        for model in [Number, Category, Tag, Item]:
            editor.create_model(model)
    
    # Run test
    test_case = TestExistsExclude()
    test_case.setUp()
    try:
        test_case.test_exists_exclude()
        print("All tests passed!")
    except Exception as e:
        print(f"Test failed: {type(e).__name__}: {e}")