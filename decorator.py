import functools

def repeat(n):
    """
    Usage:
    
    > @repeat(3)
    > def print_something(something):
    >     print(something)
    
    > print_something('123')
    123
    123
    123
    
    """
    def decorator(f)
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            for i in range(n):
                f(*args, **kwargs)
        return wrapper_demo
    return decorator
