# -*- coding: utf8
import os
import shutil

import options
from system.lib.tools import getLogger
from system.lib import hashing
from system.platforms.os import OsPlatform
from system.lib.decorators import before_after


class BaseServicePlatform(object):
    def __init__(self, host_server, attributes):
        """
        @type host_server: OsPlatform
        @type attributes: dict
        """
        self.platform_alias = self.__class__.__name__.lower()
        self.logger = getLogger(self.platform_alias)

        # Кастомные данные, которые необходимо отправлять воркеру в ответ на выполненное задание
        self.response_data = dict()

        # Operate with current service as OS-system-service
        self.service_mode = True

        # Нужна ли локальная учетная запись пользователя в системе при установке сервиса
        self.need_local_user = True

        # Класс-хелпер. В основном, для выполнения шелл команд нужен здесь
        self.host_server = host_server

        # Весь набор пришедших из очереди атрибутов
        self.attributes = attributes

        # Конфиг будет парситься сюда
        self.parsed_config = None

        # Информация о пользователе-владельце устанавливаемого сервиса
        self.user_info = attributes.get("account", dict())

        # Параметры установленного сервера (таблица services)
        self.service_info = attributes.get("service", dict())

        # Параметры платформы (таблица platforms)
        self.platform_info = attributes.get("platform", dict())

        # Параметры хост-сервера (таблица hosts)
        if "host_info" in attributes.keys():
            self.host_info = attributes.get("host", dict())

        self._setup_variables()

        # Инициализацию и дальнейшую настройку унаследованных от этого класса модулей можно производить здесь
        if hasattr(self, 'init'):
            self.init()

        self.logger.info("%s helper initialized." % type(self).__name__)

    def _setup_variables(self):
        # Current service root name
        self.service_name = "%s_%s" % (self.platform_alias, self.service_info["id"])

        self.service_root = "/home/%(user)s/%(alias)s_%(id)s" % dict(
            user=self._get_user_name(),
            alias=self.platform_info["alias"],
            id=self.service_info["id"]
        )

    def _get_user_name(self):
        return "%s%s" % (self.user_info['nick_name'], options.user_name_suffix)

    def check_system_user(self, user_name, user_password):
        # Проверяем наличие пользователя в системе
        self.logger.info("Checking for user %s exists" % user_name)
        if not self.host_server.get_user_info(user_name):
            self.logger.warn("User not found, trying to create")
            # Если не получилось создать пользователя, говорим об этом сайту
            if not self.host_server.create_user(user_name, user_password):
                self.log_and_throw("Failed to create system user: %s" % self.host_server.exec_result.stderr)
            else:
                self.logger.info("Successfully created new user %s" % user_name)
        else:
            self.logger.info("The user %s is already exists" % user_name)

    def before_reinstall(self):
            self.logger.warn("BeforeReinstall is not implemented, skipping...")

    def before_reinstall(self):
        self.logger.warn("BeforeReinstall is not implemented, skipping...")

    def after_reinstall(self):
        self.logger.warn("AfterInstall is not implemented, skipping...")

    def before_install(self):

        self.logger.info("Checking if need create local user...")
        if self.need_local_user:
            self.check_system_user(self._get_user_name(), self.user_info['password'])

        self.logger.warn("Checking for service root exists...")
        if not os.path.exists(self.service_root):
            self.logger.warn("Service root not found. Creating...")
            if self.host_server.execute(options.cmd_create_service_root % dict(user=self._get_user_name(),
                                                                               service_root=self.service_root)):
                self.logger.info("Successfully created!")
            else:
                self.log_and_throw("Failed to create %s" % self.service_root)


    def after_install(self):
        self.logger.warn("AfterInstall is not implemented, skipping...")

    def before_start(self):
        real_hash = hashing.file_get_sha1("/home/%(user)s/%(alias)s_%(server_id)s/%(platform_executable_name)s" % {
            "user": self._get_user_name(),
            "alias": self.platform_info["alias"],
            "server_id": self.service_info["id"],
            "platform_executable_name": self.platform_info["executable_name"]
        })
        if real_hash != self.platform_info['executable_hash']:
            raise Exception("Service executable corrupted or missing! Expected:%s,  got:%s" % (
                self.platform_info["executable_hash"], real_hash))
        else:
            self.logger.info("Executable hash check success!")
        if hasattr(self, 'sync_config'):
            meth = getattr(self, 'sync_config')
            meth()

    def after_start(self):
        self.logger.warn("AfterStart is not implemented, skipping...")

    def before_stop(self):
        self.logger.warn("BeforeStop is not implemented, skipping...")

    def after_stop(self):
        self.logger.warn("AfterStop is not implemented, skipping...")

    def before_uninstall(self):
        self.logger.warn("BeforeUninstall is not implemented, skipping...")

    def after_uninstall(self):
        self.logger.warn("AfterUninstall is not implemented, skipping...")

    def run_script(self, name):
        return self.host_server.runScript(name, self.platform_alias, self.attributes,
                                          local_user_name=self._get_user_name())

    def get_slot_count(self):
        pass

    def get_port(self):
        pass

    def get_rcon(self):
        pass

    def get_pid(self):
        pid = None
        if self.service_mode:
            pid = self.host_server.getServiceManager(self.service_name).getPid()
        else:
            response = self.run_script("get_pid")
            pid = int(response.stdout)
        self.response_data["pid"] = pid

    def get(self):
        pass

    def set(self):
        pass

    def install_service(self):
        manager = self.host_server.getServiceManager(self.service_name)
        service_config = self.host_server.compileTemplate('service_template', self.platform_alias, self.attributes)
        manager.install(service_config)

    @before_after(before=before_install, after=after_install)
    def install(self):
        self.logger.info("Installing service %s " % self.service_name)

        self.run_script("install")

        if self.service_mode:
            self.install_service()


    def uninstall_service(self):
        manager = self.host_server.getServiceManager(self.service_name)
        manager.uninstall()

    @before_after(before=before_uninstall, after=after_uninstall)
    def uninstall(self):
        self.logger.info("Uninstalling service %s" % self.service_name)

        self.stop()

        self.run_script('uninstall')
        if self.service_mode:
            self.uninstall_service()

        if self.host_server.get_user_info(self._get_user_name()):
            if "delete_sys_account" in self.attributes.keys() and self.attributes['delete_sys_account']:
                self.logger.warn("Removing account %(user)s from this server" % {
                    "user": self._get_user_name()
                })
                try:
                    self.host_server.execute(options.cmd_kill_users_services % {
                        "user": self._get_user_name()
                    })
                except:
                    pass

                self.host_server.execute(options.cmd_delete_user % {
                    "user": self._get_user_name()
                })
        else:
            self.logger.info("System account was removed before... Skipping...")


    @before_after(before=before_reinstall, after=after_reinstall)
    def reinstall(self):
        self.stop()

        for f in os.listdir(self.service_root):
            fpath = os.path.join(self.service_root, f)

            if os.path.isfile(fpath):
                os.unlink(fpath)
            elif os.path.isdir(fpath):
                shutil.rmtree(fpath)

        self.install()


    @before_after(before=before_start, after=after_start)
    def start(self):

        self.logger.info("Starting service %s" % self.service_name)
        if self.service_mode:
            pid = self.host_server.getServiceManager(self.service_name).start(service_info=self.service_info)
            self.response_data["pid"] = pid
        else:
            self.run_script("start")


    @before_after(before=before_stop, after=after_stop)
    def stop(self):
        self.logger.info("Stopping service %s" % self.service_name)
        if self.service_mode:
            return self.host_server.getServiceManager(self.service_name).stop(service_info=self.service_info)
        else:
            for i in xrange(3):
                try:
                    success = self.host_server.execute(""" sudo /bin/sh -c 'ps cax| grep %(pid)s 2>/dev/null' """ % {
                        "pid": self.service_info['pid']
                    })
                    if success:
                        self.host_server.execute(""" sudo -u %(username)s  -H /bin/sh -c 'kill -9 %(pid)s' """ % {
                            "username": self._get_user_name(),
                            "pid": self.service_info['pid']
                        })
                        self.host_server.sleep(1)
                except:
                    return True
            raise Exception("Failed to kill process with id %(pid)s for user %(username)s" % {
                "username": self._get_user_name(),
                "pid": self.service_info['pid']
            })

    def log_and_throw(self, message, level="fatal", exception=Exception):
        level = getattr(self.logger, level)
        level(message)
        raise exception(message)

