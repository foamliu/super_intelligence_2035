import pytest

@pytest.mark.foo
class Foo:
    pass


@pytest.mark.bar
class Bar:
    pass


class TestDings(Foo, Bar):
    def test_dings(self, request):
        # Check class markers
        class_markers = [m.name for m in request.node.parent.own_markers]
        assert "foo" in class_markers
        assert "bar" in class_markers
        # Check keywords
        assert "foo" in request.node.keywords
        assert "bar" in request.node.keywords
        # Check all markers including inherited
        all_markers = [m.name for m in request.node.iter_markers()]
        assert "foo" in all_markers
        assert "bar" in all_markers
