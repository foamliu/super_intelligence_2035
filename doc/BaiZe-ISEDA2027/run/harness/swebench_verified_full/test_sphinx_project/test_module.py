from typing import Tuple

def foo() -> Tuple[()]:
    """Sample function that returns an empty tuple."""
    return ()

def bar() -> Tuple[int, str]:
    """Sample function that returns a normal tuple."""
    return (1, "hello")
