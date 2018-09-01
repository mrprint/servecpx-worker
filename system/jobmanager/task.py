__author__ = 'nolka'


class BaseTask(object):

    @property
    def id(self):
        return self._id

    @property
    def result(self):
        return self._result

    @property
    def code(self):
        return self._code

    @property
    def is_success(self):
        if self.code == 0:
            return True
        return False

    def __init__(self, index=None, **kwargs):
        self._id = index
        self._result = None
        self._code = None
        if isinstance(kwargs, dict):
            self.__dict__.update(kwargs)
        elif isinstance(kwargs, (str, unicode)):
            self.data = kwargs

    def run(self):
        raise NotImplementedError("Run method is not implemented yet!")

    def success(self, result):
        self._result = result

    def failed(self, code=500, message=None):
        self._code = code
        self._result = message

    def set_id(self, value):
        self._id = value


class SimpleTask(BaseTask):
    pass


class PoisonTask(BaseTask):
    pass