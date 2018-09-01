__author__ = 'nolka'

import config
from system.lib.tools import getLogger


def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


def log_call(fn):
    l = getLogger()

    def wrapper(*args, **kwargs):
        l.log("Executing method: %s" % fn.__name__)
        return fn(*args, **kwargs)
    return wrapper


def before_after(before=None, after=None):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if before is not None:
                before(self)
            result = func(self, *args, **kwargs)
            if after is not None:
                after(self)
            return result
        return wrapper
    return decorator
