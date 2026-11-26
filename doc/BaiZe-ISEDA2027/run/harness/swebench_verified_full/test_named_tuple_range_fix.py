"""
Test that named tuples used as arguments to __range filters work correctly.
"""
from collections import namedtuple
import django
from django.conf import settings
from django.db import models
from django.test import TestCase

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

# Create a test model
class TestModel(models.Model):
    value = models.IntegerField()
    
    class Meta:
        app_label = 'test'

# Create database tables
from django.db import connection
with connection.schema_editor() as editor:
    editor.create_model(TestModel)

# Create test data
TestModel.objects.create(value=1)
TestModel.objects.create(value=5)
TestModel.objects.create(value=10)
TestModel.objects.create(value=15)

# Define a named tuple for range
Range = namedtuple('Range', ['near', 'far'])

class NamedTupleRangeTest(TestCase):
    def test_named_tuple_range_filter(self):
        """Test that named tuples work correctly with __range filters"""
        # This should not raise TypeError anymore
        range_tuple = Range(near=3, far=12)
        results = TestModel.objects.filter(value__range=range_tuple)
        
        # Should return values 5 and 10
        self.assertEqual({obj.value for obj in results}, {5, 10})
        
        # Test with regular tuple for comparison
        regular_results = TestModel.objects.filter(value__range=(3, 12))
        self.assertEqual({obj.value for obj in regular_results}, {5, 10})
        
        print("✅ Named tuple range filter works correctly!")
    
    def test_list_range_filter(self):
        """Test that lists still work correctly with __range filters"""
        results = TestModel.objects.filter(value__range=[3, 12])
        self.assertEqual({obj.value for obj in results}, {5, 10})
        print("✅ List range filter works correctly!")
    
    def test_regular_tuple_range_filter(self):
        """Test that regular tuples still work correctly with __range filters"""
        results = TestModel.objects.filter(value__range=(3, 12))
        self.assertEqual({obj.value for obj in results}, {5, 10})
        print("✅ Regular tuple range filter works correctly!")

if __name__ == '__main__':
    # Run tests
    test = NamedTupleRangeTest()
    test.test_named_tuple_range_filter()
    test.test_list_range_filter()
    test.test_regular_tuple_range_filter()
    print("\n🎉 All tests passed! The fix is working correctly.")
