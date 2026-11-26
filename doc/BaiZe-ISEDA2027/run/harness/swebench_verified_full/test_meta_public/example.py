public_var = 42  #: This is a public variable.
_foo = None  #: :meta public:
_foo_with_doc = None  #: This is a private variable with docstring, no public meta.

def _bar():
    """This is a test function.

    :meta public:
    """
    pass
