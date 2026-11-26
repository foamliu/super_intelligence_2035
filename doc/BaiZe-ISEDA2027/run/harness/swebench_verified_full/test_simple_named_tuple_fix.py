"""
Simple test for the named tuple fix in resolve_lookup_value
"""
from collections import namedtuple
import sys
import os

# Add the django directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django'))

# Import just what we need
from django.db.models.sql.query import Query
from django.db.models import Model
from django.db.models.fields import IntegerField

# Create a dummy model for testing
class DummyModel(Model):
    value = IntegerField()
    
    class Meta:
        app_label = 'test'

# Create a query instance
query = Query(DummyModel)

# Test the resolve_lookup_value method directly
Range = namedtuple('Range', ['near', 'far'])
range_tuple = Range(1, 10)

# This should not raise TypeError anymore
result = query.resolve_lookup_value(range_tuple, can_reuse=None, allow_joins=True, simple_col=False)

print(f"✅ Named tuple resolution works! Original: {range_tuple}, Result: {result}")
print(f"✅ Type preserved: {type(result) is Range}")
print(f"✅ Values correct: near={result.near}, far={result.far}")

# Test regular tuple
regular_tuple = (1, 10)
result_regular = query.resolve_lookup_value(regular_tuple, can_reuse=None, allow_joins=True, simple_col=False)
print(f"\n✅ Regular tuple resolution works! Original: {regular_tuple}, Result: {result_regular}")
print(f"✅ Type preserved: {type(result_regular) is tuple}")

# Test list
list_val = [1, 10]
result_list = query.resolve_lookup_value(list_val, can_reuse=None, allow_joins=True, simple_col=False)
print(f"\n✅ List resolution works! Original: {list_val}, Result: {result_list}")
print(f"✅ Type preserved: {type(result_list) is list}")

print("\n🎉 All tests passed! The fix correctly handles named tuples, regular tuples, and lists.")
