class Test:
    #: This is a public class variable.
    public_var = 42

    #: :meta public:
    _private_var = 123

    def __init__(self):
        #: :meta public:
        self._instance_var = 456

    def public_method(self):
        """Public method."""
        pass

    def _private_method(self):
        """Private method with :meta public:.

        :meta public:
        """
        pass
