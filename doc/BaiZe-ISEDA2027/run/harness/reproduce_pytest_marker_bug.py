import itertools
import pytest

# Original behavior test
@pytest.mark.foo
class Foo:
    pass

@pytest.mark.bar
class Bar:
    pass

class TestDings(Foo, Bar):
    def test_dings(self):
        pass

# Test with metaclass fix
class BaseMeta(type):
    @property
    def pytestmark(self):
        return (
            getattr(self, "_pytestmark", []) +
            list(itertools.chain.from_iterable(getattr(x, "_pytestmark", []) for x in self.__mro__))
        )

    @pytestmark.setter
    def pytestmark(self, value):
        self._pytestmark = value

class Base(metaclass=BaseMeta):
    pass

@pytest.mark.foo
class Foo2(Base):
    pass

@pytest.mark.bar
class Bar2(Base):
    pass

class TestDings2(Foo2, Bar2):
    def test_dings2(self):
        pass

def test_check_markers():
    # Check original behavior
    # Get markers for TestDings
    markers_original = getattr(TestDings, 'pytestmark', [])
    if not isinstance(markers_original, (list, tuple)):
        markers_original = [markers_original]
    marker_names_original = [m.name for m in markers_original]
    print(f"Original TestDings markers: {marker_names_original}")
    assert 'foo' in marker_names_original, "foo marker missing in original"
    # This will fail in pytest 3-6 (and 7.x as we see)
    assert 'bar' in marker_names_original, "bar marker missing in original (this is the bug)"
    
    # Check fixed behavior
    markers_fixed = getattr(TestDings2, 'pytestmark', [])
    if not isinstance(markers_fixed, (list, tuple)):
        markers_fixed = [markers_fixed]
    marker_names_fixed = [m.name for m in markers_fixed]
    print(f"Fixed TestDings2 markers: {marker_names_fixed}")
    assert 'foo' in marker_names_fixed, "foo marker missing in fixed"
    assert 'bar' in marker_names_fixed, "bar marker missing in fixed"
