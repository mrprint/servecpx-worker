__author__ = 'nolka'

import string
import random
import logging

import options

def getLogger(name, log_file=None, log_indent=0, **kwargs):

    if name in logging.Logger.manager.loggerDict.keys():
        return logging.Logger.manager.loggerDict.get(name)

    base_indent=log_indent

    if 'format' not in kwargs.keys():
        #"%(asctime)s %(levelname)-8s %(filename)s(%(lineno)d): %(name)-18s: '+(" "*self.base_indent)+'%(message)s"
        log_format = "%(asctime)s %(levelname)-8s %(filename)s(%(lineno)d):\t %(name)-18s: "+(" "*base_indent)+"%(message)s"
        #self.log_format = '[%(asctime)s] [%(levelname)s] %(filename)s(%(lineno)d): '+(" "*self.base_indent)+'%(message)s'
    else:
        log_format = kwargs.get('format')

    logger = logging.getLogger(name)
    logger.setLevel(options.log_level)

    # log_formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(filename)s(%(lineno)d): %(name)-18s: %(message)s")

    log_formatter = logging.Formatter(log_format)

    general_log = logging.FileHandler("%s/general_log" % options.log_dir)
    console_log = logging.StreamHandler()
    if "log_file" in kwargs.keys() and kwargs.get("log_file") is not None:
        file_log = logging.FileHandler("%s/%s" % (options.log_dir, kwargs.get("log_file")))
        file_log.setFormatter(log_formatter)
        logger.addHandler(file_log)

    general_log.setFormatter(log_formatter)
    console_log.setFormatter(log_formatter)

    logger.addHandler(console_log)
    logger.addHandler(general_log)
    return logger

def random_str(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))
