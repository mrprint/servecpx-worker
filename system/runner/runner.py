"""Runner module - is a mechanism for executing different programs using single entry point and code base.


.. module:: runner
    :platform: Unix, Windows
.. moduleauthor:: nolka aka xternalx<xternalx@ya.ru>
"""
# -*- coding: utf8

__docformat__ = 'reStructuredText'

import importlib


class Runner(object):
    """
    Runner - instantiates class, which name passed in script command line(by default),
    then calls method :func:`run` from them
    """

    def __init__(self, modules_path):
        """
        Constructor

        :param modules_path: Path to load modules
        :type modules_path: str
        """
        self.modules_path = modules_path

    @classmethod
    def _get_runnable(cls, what_to_import, runnable_type_name):
        """
        Class method, which import type from module, instantiate, and inject dependencies to them.

        :param what_to_import: module or package name, from where type will be imported
        :param runnable_type_name: type name of runnable to be imported and instantiated

        :type what_to_import: str
        :type runnable_type_name: str
        :return: :class:`BaseRunnable`
        """
        _module = importlib.import_module(what_to_import)
        _runnable = getattr(_module, runnable_type_name)
        return _runnable(_runnable.get_cmdline_parser(), _runnable.get_logger())

    def run(self, runnable_name):
        """
        Create and execute passed runnable_name

        :param runnable_name: Runnable to be executed
        :type runnable_name: str
        :return None:
        """
        if "." in runnable_name:
            module_to_import, handler_name = runnable_name.rsplit(".", 1)
            what_to_import = "{0}.{1}".format(self.modules_path, module_to_import)
            runnable_instance = self._get_runnable(what_to_import, handler_name)
        else:
            runnable_instance = self._get_runnable(self.modules_path, runnable_name)

        runnable_instance.run()


class BaseRunnable(object):
    """
    Base runnable class
    """
    def __init__(self, cmdline_options, logger):
        """
        Constructor takes two args - parsed command line arguments, and logger instance

        :param cmdline_options: :class:`argparse.Namespace`
        :param logger: Logger class with implemented methods: indo, debug, error, fatal
        """
        self.options = cmdline_options
        self.logger = logger
        self.logger.info("Initialized")

    def run(self):
        """
        Main method to be executed by :class:`Runner`

        :return:
        """
        raise NotImplementedError("Runnable is not implemented in " + self.__class__.__name__)

    @staticmethod
    def get_cmdline_parser():
        """
        This method will required for command line parser creation

        :return: Parsed command line args
        """
        raise NotImplementedError()

    @classmethod
    def get_logger(cls, file_name='general_log'):
        """
        Create logger object

        :param file_name: file name where log messages will be written
        :type file_name: str
        :return:
        """
        raise NotImplementedError()
