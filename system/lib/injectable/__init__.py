__author__ = 'nolka'

import logging
from logging.handlers import RotatingFileHandler

import options

def inject_logger(instance, name=None, file_name=None, log_to_file=True, try_log_namespace=False):

        if name is None:
            name = instance.__class__.__name__
            if try_log_namespace and hasattr(instance, "namespace"):
                name = "%s.%s" % (instance.namespace, name)

        # check if logger already exists
        if name in logging.Logger.manager.loggerDict.keys():
            return logging.getLogger(name)

        log_formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(pathname)s->%(name)s:%(lineno)-4d: %(message)s")
        console_log = logging.StreamHandler()

        if log_to_file:
            if file_name is None:
                file_name = name
            file_log = RotatingFileHandler("%s/logs/%s" % (options.ROOT, file_name), maxBytes=100*1024*1024, backupCount=10)

        console_log.setFormatter(log_formatter)
        file_log.setFormatter(log_formatter)

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(console_log)
        logger.addHandler(file_log)

        return logger