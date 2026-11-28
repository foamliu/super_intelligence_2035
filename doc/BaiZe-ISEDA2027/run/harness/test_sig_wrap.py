import inspect
import functools

class QuerySet:
    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        pass

def create_method(name, method):
    @functools.wraps(method)
    def manager_method(self, *args, **kwargs):
        return getattr(self.get_queryset(), name)(*args, **kwargs)
    return manager_method

class Manager:
    @classmethod
    def _get_queryset_methods(cls, queryset_class):
        new_methods = {}
        for name, method in inspect.getmembers(queryset_class, predicate=inspect.isfunction):
            if hasattr(cls, name):
                continue
            new_methods[name] = create_method(name, method)
        return new_methods
    
    def get_queryset(self):
        return QuerySet()

MyManager = type('MyManager', (Manager,), Manager._get_queryset_methods(QuerySet))
m = MyManager()

print("Signature:", inspect.signature(m.bulk_create))
print("Expected: (objs, batch_size=None, ignore_conflicts=False)")
print("Has __wrapped__:", hasattr(m.bulk_create, '__wrapped__'))
if hasattr(m.bulk_create, '__wrapped__'):
    print("Wrapped signature:", inspect.signature(m.bulk_create.__wrapped__))
