import sys
sys.path.insert(0, '/home/app.e0031982/.local/lib/python3.10/site-packages')

from _pytest.mark.structures import get_unpacked_marks
import pytest

@pytest.mark.foo
class Foo:
    pass

@pytest.mark.bar
class Bar:
    pass

class TestDings(Foo, Bar):
    pass

# Let's see what get_unpacked_marks returns
marks = get_unpacked_marks(TestDings)
mark_names = [m.name for m in marks]
print(f"get_unpacked_marks(TestDings) returned: {mark_names}")

print(f"\nTestDings.__dict__ has pytestmark: {'pytestmark' in TestDings.__dict__}")
print(f"Foo.__dict__ has pytestmark: {'pytestmark' in Foo.__dict__}")
print(f"Bar.__dict__ has pytestmark: {'pytestmark' in Bar.__dict__}")

print(f"\nFoo.__dict__['pytestmark']: {Foo.__dict__['pytestmark']}")
print(f"Bar.__dict__['pytestmark']: {Bar.__dict__['pytestmark']}")

print(f"\nTestDings.__mro__: {[c.__name__ for c in TestDings.__mro__]}")
