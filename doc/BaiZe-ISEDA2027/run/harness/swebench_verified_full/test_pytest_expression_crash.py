import pytest

# Test the Expression.compile crash
def test_expression_compile_false():
    from _pytest.mark.expression import Expression
    expr = Expression.compile("False")
    # The matcher function: if the identifier is "False", return False
    result = expr.evaluate(lambda ident: ident == "False")
    # Wait no: the expression "False" evaluates to the value of the identifier "False"
    # So if our matcher returns True for "False", then result will be True
    result = expr.evaluate(lambda ident: True if ident == "False" else False)
    assert result == True
    # Test with a matcher that returns False for "False"
    result = expr.evaluate(lambda ident: False if ident == "False" else True)
    assert result == False
