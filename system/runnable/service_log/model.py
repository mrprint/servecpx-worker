import os
import re


class BaseModel(object):
    @classmethod
    def parse(cls, msg_line):
        """

        :param msg_line:
        :type msg_line: str
        :return:
        """
        result = re.match(cls.get_pattern(), msg_line.strip())
        if result:
            instance = cls()
            for k, v in result.groupdict().iteritems():
                setattr(instance, k, v)
            return instance
        raise ValueError("Unknown model record passed!")


class LogFileModel(BaseModel):
    __slots__ = ['service_id', 'file_name', '_fh']

    @classmethod
    def get_pattern(cls):
        return r"^(?P<service_id>[\d]+)\s(?P<file_name>.+)"

    def exists(self):
        return os.path.exists(self.file_name)

    @property
    def handle(self):
        if not self._fh:
            self._fh = open(self.file_name, 'r')
        return self._fh

    def __str__(self):
        return " ".join((self.service_id, self.file_name))
