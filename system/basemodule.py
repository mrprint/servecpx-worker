class BaseModule(object):
    __slots__ = ["_manager", "logger", "namespace"]

    def __init__(self, manager, logger, **kwargs):
        self._manager = manager
        self.logger = logger

    def before_command(self, cmd):
        return True

    def after_command(self, cmd, result):
        pass

    def on_loaded(self):
        pass

    def on_command(self, cmd, *args, **kwargs):
        pass

    def get_full_name(self):
        return "%s.%s" % (self.namespace, type(self).__name__)

    def log_and_throw(self, message, level="fatal", exception=Exception):
        level = getattr(self.logger, level)
        level(message)
        raise exception(message)