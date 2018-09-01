__author__ = 'nolka'

import requests

from ..worker import BaseWorker
from ..task import SimpleTask


class UrlParser(BaseWorker):
    def execute(self, task):
        """
        :type url: SimpleTask
        """

        result = requests.get('%s' % task.data)

        if result.status_code == 200:
            return len(result.text)


class NamedUrlParser(UrlParser):
    def __init__(self, name):
        self.name = name
