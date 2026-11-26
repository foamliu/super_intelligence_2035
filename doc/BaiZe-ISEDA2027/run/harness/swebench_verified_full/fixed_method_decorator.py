from functools import wraps, update_wrapper


def method_decorator(decorator):
    """
    A fixed implementation of method_decorator that preserves original function attributes
    when applying decorators to class methods.
    
    Fixes the issue where decorated function receives a partial object without __name__,
    __module__ or __doc__ attributes.
    
    Args:
        decorator: The decorator function to apply to class methods
        
    Returns:
        Wrapped decorator that works correctly on class methods
    """
    def _method_decorator(func):
        # Apply the decorator ONCE to the original function at definition time
        # This ensures the decorator receives the actual function, not a partial
        decorated_func = decorator(func)
        
        # Wrap the decorated function to handle the self parameter
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return decorated_func(self, *args, **kwargs)
        
        return wrapper
    return _method_decorator


# If you need to support decorators that expect bound methods (legacy use case),
# use this alternative implementation that properly copies attributes to partials:
def method_decorator_legacy_compat(decorator):
    def _method_decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Create bound partial and copy all original function attributes to it
            bound_func = partial(func, self)
            update_wrapper(bound_func, func)
            # Apply decorator to the bound partial for each call
            return decorator(bound_func)(*args, **kwargs)
        return wrapper
    return _method_decorator


# Test case to verify the fix
if __name__ == "__main__":
    from functools import wraps
    
    def logger(func):
        @wraps(func)
        def inner(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                result = str(e)
            finally:
                print(f"{func.__name__} called with args: {args} and kwargs: {kwargs} resulting: {result}")
            return result
        return inner
    
    class Test:
        @method_decorator(logger)
        def hello_world(self):
            return "hello"
        
        @method_decorator(logger)
        def add(self, a, b):
            return a + b
    
    # Test that no AttributeError is thrown
    t = Test()
    assert t.hello_world() == "hello"
    assert t.add(2, 3) == 5
    
    print("All tests passed! No AttributeError from partial object.")
