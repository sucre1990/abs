from functools import wraps


def memorize(f):
    cache = f.cache = {}

    @wraps(f)
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = f(*args, **kwargs)
        return cache[key]

    return wrapper
