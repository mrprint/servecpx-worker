#!/usr/bin/python
__author__ = 'nolka'

import sys
import importlib

reload(sys)
sys.setdefaultencoding('utf-8')

from system.logger import Logger


def get_runnable(what_to_import, runnable_type_name):
    _module = importlib.import_module(what_to_import)
    _runnable = getattr(_module, runnable_type_name)
    return _runnable(_runnable.get_cmdline_parser(), Logger(runnable_type_name, file_name=_runnable.get_logger()))


def main(modules_path, runnable_name):
    if "." in runnable_name:
        module_to_import, handler_name = runnable_name.rsplit(".", 1)
        what_to_import = "{0}.{1}".format(modules_path, module_to_import)
        runnable_instance = get_runnable(what_to_import, handler_name)
    else:
        runnable_instance = get_runnable(modules_path, runnable_name)

    runnable_instance.run()


if __name__ == "__main__":
    modules_path = "system.runnable"

    if len(sys.argv) < 2:
        raise RuntimeError("No module name specified to run!")

    main(modules_path, sys.argv[1])


