class Base:
    """Base class."""
    
    #: This is an inherited attribute from Base class
    inherited_attr = 42
    
    def base_method(self):
        """Base method."""
        pass

class Derived(Base):
    """Derived class that inherits from Base."""
    
    #: This is a derived attribute
    derived_attr = "hello"
    
    def derived_method(self):
        """Derived method."""
        pass
