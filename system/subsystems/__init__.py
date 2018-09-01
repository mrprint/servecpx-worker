__author__ = 'nolka'

from importlib import import_module
from system.lib.tools import getLogger

class Factory(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Factory, cls).__new__(cls, *args, **kwargs)
            cls._instance.logger = getLogger("SubsystemFactory", "general_log")
        return cls._instance

    def create(self, subsys_name, *args, **kwargs):
        self.logger.debug("Creating: %s" % subsys_name)
        module_name = class_name = None
        if "." in subsys_name:
            module_name, class_name = subsys_name.rsplit(".", 1)
        else:
            class_name = subsys_name

        if module_name is not None:
            module = import_module(module_name)
            cls = getattr(module, class_name, None)
            if cls is None:
                klass = cls(*args, **kwargs)
                if "inject" in kwargs.keys():
                    for attr, value in kwargs.get("inject").iteritems():
                        setattr(klass, attr, value)
                    kwargs.pop("inject", None)

                return klass
            else:
                self.logger.error("Failed to get class named %s" % class_name)
        else:
            self.logger.error("Failed instantiate class without module name!")


class Subsystem(object):
    def run(self):
        pass

