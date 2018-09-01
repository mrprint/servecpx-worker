__author__ = 'nolka'

class SimpleTask(object):
    # __slots__ = ('id', 'instance', 'method_name', 'method_args', 'method_kwargs')
    def __init__(self, _id, instance, method_name, *args, **kwargs):
        self.id = _id
        self.instance = instance
        self.method_name = method_name

        self.method_args = args
        self.method_kwargs = kwargs

    def run(self):
        method = getattr(self.instance, self.method_name)
        return method(*self.method_args, **self.method_kwargs)