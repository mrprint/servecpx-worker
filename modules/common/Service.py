# -*- coding: utf8
__author__ = 'nolka'

from importlib import import_module

from system.platforms.os import OsPlatform
from system.platforms.services import BaseServicePlatform
from system.basemodule import BaseModule
import options as config


class Service(BaseModule):

    def __init__(self, manager, *args, **kwargs):
        super(Service, self).__init__(manager, *args, **kwargs)
        self.host_server = None
        " :type : OsPlatform "

    def before_command(self, cmd):
        self.host_server = OsPlatform(config.host_os_service_initializer)
        return True

    def after_command(self, cmd, result):
        # self.host_server.cd(config.work_dir)
        pass

    def _get_helper(self, attributes=dict(), host_server=None):
        """
        :rtype: BaseServicePlatform
        """

        platform_name = attributes["platform"]["alias"]
        self.logger.info("Creating helper...")
        service_platform_module = import_module("system.platforms.services.%s" % platform_name)
        helper_class = getattr(service_platform_module, platform_name.capitalize(), None)

        if not helper_class:
            self.log_and_throw("Helper %s was not found" % platform_name.capitalize())
        return helper_class(self.host_server, attributes)

    # Запуск сервера
    def cmd_start(self, attributes):
        self.logger.info("Running Start action...")
        service_platform = self._get_helper(attributes)
        service_platform.start()
        return service_platform.response_data

    # Получение PID запущенного сервера
    def cmd_getPid(self, attributes):
        self.logger.info("Running GetPid action...")
        service_platform = self._get_helper(attributes)
        service_platform.get_pid()
        return service_platform.response_data

    # Остановка
    def cmd_stop(self, attributes):
        self.logger.info("Running Stop action...")
        self.logger.info("Stopping service id:%s..." % attributes['service'].get('id'))
        service_platform = self._get_helper(attributes)
        service_platform.stop()
        return service_platform.response_data

    # Установка
    def cmd_install(self, attributes):
        self.logger.info("Running Install action...")
        service_platform = self._get_helper(attributes)
        service_platform.install()
        return service_platform.response_data

    # Удаление
    def cmd_uninstall(self, attributes):
        self.logger.info("Running Uninstall action...")
        service_platform = self._get_helper(attributes)
        service_platform.uninstall()
        return service_platform.response_data

    # Переустановка сервера. ПРи этом сохраняется оригинальный каталог сервера, и его id.
    # Фактически из каталога с игрой удаляются все файлы, и туда заново распаковываются файлы сервера
    def cmd_reinstall(self, attributes):
        self.logger.info("Running Restore action...")
        platform = self._get_helper(attributes)
        platform.reinstall()
        return platform.response_data
