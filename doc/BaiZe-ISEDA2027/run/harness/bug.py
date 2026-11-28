import pytest

@pytest.mark.parametrize("a", ["..["])
def test_boo(a):
    assert 0
