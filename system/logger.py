__author__ = 'nolka'

import logging
from logging.handlers import RotatingFileHandler

import options


class Logger(object):
    __slots__ = ["_logger"]

    def __init__(self, name=None, file_name=None, log_to_file=True):
        if name is None:
            name = "Logger-%d" % id(self)

        # check if logger already exists
        if name in logging.Logger.manager.loggerDict.keys():
            logger = logging.getLogger(name)
        else:
            log_formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(pathname)s->%(name)s:%(lineno)-4d: %(message)s")
            console_log = logging.StreamHandler()

            if log_to_file:
                if file_name is None:
                    file_name = name
                file_log = RotatingFileHandler("%s/logs/%s" % (options.ROOT, file_name), maxBytes=100*1024*1024, backupCount=10)
                file_log.setFormatter(log_formatter)

            console_log.setFormatter(log_formatter)

            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)
            logger.addHandler(console_log)

            if log_to_file:
                logger.addHandler(file_log)

        self._logger = logger

    # def __call__(self, method, *args, **kwargs):
    #     _m = getattr(self._logger, method)
    #     return _m(*args, **kwargs)

    def __getattr__(self, item):
        return getattr(self._logger, item)

