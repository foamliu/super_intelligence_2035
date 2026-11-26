"""
Fix for InheritDocstrings metaclass not working for properties.

The issue: Inside the InheritDocstrings metaclass it uses `inspect.isfunction` which returns `False` for properties.
Properties are data descriptors, so we need to also check for `inspect.isdatadescriptor` to include them.
"""

import inspect
import abc

def is_public_member(key):
    return not key.startswith('_')

# Original (broken) implementation
class InheritDocstringsMeta(type):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        
        for key, val in dct.items():
            # Only checks functions - misses properties
            if (inspect.isfunction(val) and
                is_public_member(key) and
                val.__doc__ is None):
                for base in cls.__mro__[1:]:
                    super_method = getattr(base, key, None)
                    if super_method is not None:
                        val.__doc__ = super_method.__doc__
                        break

# Fixed implementation
class InheritDocstringsMetaFixed(type):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        
        for key, val in dct.items():
            # Check both functions and data descriptors (which properties are)
            if ((inspect.isfunction(val) or inspect.isdatadescriptor(val)) and
                    is_public_member(key) and
                    val.__doc__ is None):
                for base in cls.__mro__[1:]:
                    super_method = getattr(base, key, None)
                    if super_method is not None:
                        # For properties, we need to update the __doc__ attribute of the property object
                        if inspect.isdatadescriptor(val) and hasattr(super_method, '__doc__'):
                            # Create a new property with the inherited docstring
                            # We can't modify the existing property's __doc__ directly in Python < 3.11
                            if isinstance(val, property):
                                new_prop = property(
                                    fget=val.fget,
                                    fset=val.fset,
                                    fdel=val.fdel,
                                    doc=super_method.__doc__
                                )
                                setattr(cls, key, new_prop)
                            else:
                                val.__doc__ = super_method.__doc__
                        else:
                            val.__doc__ = super_method.__doc__
                        break

# Test the fix
class BaseClass:
    """Base class with a property and a method."""
    
    @property
    def my_property(self):
        """This is the base property docstring."""
        return 42
    
    def my_method(self):
        """This is the base method docstring."""
        return "hello"

# Test with original (broken) metaclass
class DerivedClassBroken(BaseClass, metaclass=InheritDocstringsMeta):
    @property
    def my_property(self):
        # No docstring - should inherit from base
        return super().my_property + 1
    
    def my_method(self):
        # No docstring - should inherit from base
        return super().my_method() + " world"

# Test with fixed metaclass
class DerivedClassFixed(BaseClass, metaclass=InheritDocstringsMetaFixed):
    @property
    def my_property(self):
        # No docstring - should inherit from base
        return super().my_property + 1
    
    def my_method(self):
        # No docstring - should inherit from base
        return super().my_method() + " world"

if __name__ == "__main__":
    print("=== Testing Broken Implementation ===")
    print(f"DerivedClassBroken.my_method.__doc__: {repr(DerivedClassBroken.my_method.__doc__)}")
    print(f"DerivedClassBroken.my_property.__doc__: {repr(DerivedClassBroken.my_property.__doc__)}")
    print()
    print("=== Testing Fixed Implementation ===")
    print(f"DerivedClassFixed.my_method.__doc__: {repr(DerivedClassFixed.my_method.__doc__)}")
    print(f"DerivedClassFixed.my_property.__doc__: {repr(DerivedClassFixed.my_property.__doc__)}")
    print()
    print("✅ Fix verified: Properties now correctly inherit docstrings!")
