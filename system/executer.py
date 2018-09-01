# -*- coding: utf8 -*-

import sys
import os
import traceback
from importlib import import_module
import inspect

from task import SimpleTask
from system.basemodule import BaseModule
from system.bus import MessageBus
from system.logger import Logger
import exceptions as exception


class Executer(object):

    __slots__ = ['_module_map', 'bus', 'logger', 'acl']

    def __init__(self, logger):
        self._module_map = {}

        self.logger = logger
        self.bus = MessageBus()

    def reinit_modules(self, dirs):
        """
        Переинициализация модулей. Старая карта модулей уничтожается, происходит заново поиск модулей, и их регистрация
        :param dirs: tuple
        :return: bool
        """
        self._module_map = {}
        for path in dirs:
            self.init_modules(path)
        return True

    def init_modules(self, modules_dir):
        """
        Выполняет загрузку модулей.
        Предполагается, что в одном модуле(файле) может находиться несколько классов-модулей,
            унаследованным от BaseModule
        :param modules_dir: str
        """
        self.logger.info("Loading modules from %s" % modules_dir)

        modules_root = "modules"

        # получили список файлов в директории с плагинами
        for plugin_file in os.listdir("%s/%s" % (modules_root, modules_dir)):
            # if "__init__" in plugin_file:
            # continue
            # если название файла заканчивается на .py, значит это исходник,
            # и его нужно добавить в список загружаемых модулей
            if not plugin_file.endswith(".py"):
                continue

            module_name = os.path.splitext(plugin_file)[0]

            self.logger.info("Searching plugin definitions in module %s..." % module_name)

            if os.path.isfile('/'.join([modules_root, modules_dir, plugin_file])):
                try:
                    module_to_import = ".".join(("%s.%s" % (modules_root, modules_dir.replace("/", ".")), module_name))
                    module = import_module(module_to_import)
                    instances_count = 0
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if inspect.isclass(obj) and issubclass(obj, BaseModule) and obj != BaseModule:
                            self.register_module(obj, module_to_import)
                            instances_count += 1
                except:
                    exc_type, exc_value = sys.exc_info()[:2]
                    self.logger.error("    ** Error loading %s(%s): %s\n%s" % (
                        plugin_file, exc_type, exc_value, traceback.format_exc()))
                finally:
                    pass
        return True

    def call_method(self, obj, method_name, *args, **kwargs):
        """
        Выполняет вызов команды модуля, по факту происходит вызов метода экземпляра объекта типа BaseModule
        :param obj: BaseModule
        :param method_name: str
        :param args: tuple
        :param kwargs: dict
        :return: mixed
        """
        callback = getattr(obj, method_name)
        return callback(*args, **kwargs)

    def is_method_exists(self, obj, method_name):
        """
        Проверяет, есть ли вызываемый метод у экземпляра модуля
        :param obj: BaseModule
        :param method_name: str
        :return: bool
        """
        if getattr(obj, method_name, None) is not None:
            return True
        return False

    def check_command_exists(self, module_instance, command):
        """
        Выполняет получение сигнатуры команды модуля
        :param module_instance: BaseModule
        :param command: str
        :return: tuple
        """
        return inspect.getargspec(getattr(module_instance, command))

    def check_command_args(self, module_instance, cmd, cmd_info, params):
        """
        Выполняет проверку переданных в команду аргументов на соответствие их сигнатуре вызываемой команды
        :param module_instance: BaseModule
        :param cmd: str
        :param cmd_info: tuple
        :param params: dict
        :return: dict
        """
        has_defaults = {}  # словарь с аргументами команды, у которой есть значения по умолчанию
        missed_args = []  # список требуемых, но не указанных аргументов в запросе
        prepared_args = {}  # сюда будем складывать аргументы, которые будут переданы вызываемой команде на вход

        # проверяем наличие атрибутов с установленными значениями по умолчанию
        if cmd_info.defaults is not None:
            # если есть, заполняем соответствующий словарь. В дальнейшем он будет использован
            # для поиска аргументов, указанных в сигнатуре функции, но отсутствующих в архументах
            # из пришедшего запроса
            has_defaults = dict(zip(reversed(cmd_info.args), reversed(cmd_info.defaults)))

        for k in cmd_info.args:
            if k in ['self']:
                pass
            elif k not in params.keys():
                if k in has_defaults.keys():
                    prepared_args[k] = has_defaults[k]
                else:
                    missed_args.append(k)
            else:
                prepared_args[k] = params[k]

        if len(missed_args) > 0:
            raise exception.BadRequestError(
                "The method '%s' called from module '%s' expected args: '%s', but it's missing" % (
                    cmd[4:], module_instance.get_full_name(), ", ".join(missed_args)))

        return prepared_args

    def register_module(self, module, route):
        """
        Регистрация модуля в карте модулей
        :param module: BaseModule
        :param route: str
        :return:
        """
        # Разворачиваем маршрут и удаляем кусок, который называн 'modules'
        route = ".".join(route.split(".")[1:-1])

        if route not in self._module_map.keys():
            self._module_map[route] = dict()

        self._module_map[route].update({module.__name__: module})

        self.logger.info("Registered type %s with route %s" % (module.__name__, route))

    def instantiate_module(self, module_name, namespace):
        """
        Создание экземпляра модуля на основе переданного имени модуля и его пространства имен
        :param module_name: str
        :param namespace: str
        :return:
        """
        if namespace not in self._module_map.keys():
            raise exception.NotImplementedError, "Namespace %s missing!" % namespace

        if module_name not in self._module_map[namespace].keys():
            raise exception.NotImplementedError, "Module %s missing" % module_name

        instance = self._module_map[namespace][module_name](self, Logger(module_name, file_name="general_log"))
        instance.namespace = namespace

        instance.on_loaded()

        return instance

    def check_access(self, app_id, route):
        print "Checking route", route
        if not self.acl.check_access(app_id, route):
            raise exception.AccessDeniedError("Access to this action is denied!")

    def get_task_data(self, cmd_data, namespace=None):
        cmd_data = cmd_data.rsplit('.', 2)

        if len(cmd_data) == 2:
            module_name, cmd = cmd_data
        elif len(cmd_data) == 3:
            namespace, module_name, cmd = cmd_data

        return module_name, namespace, cmd

    def wrap_task(self, task_id, instance, cmd, *args, **kwargs):
        """

        :param instance:
        :type instance: BaseModule
        :param cmd:
        :type cmd: str
        :param args:
        :type args: tuple
        :param kwargs:
        :type kwargs: dict
        :return: SimpleTask
        """
        task = SimpleTask(task_id, instance, cmd, *args, **kwargs)
        return task

    def execute(self, task_id, *args, **kwargs):
        """
        Выполнить команду модуля. Этот метод вызывается интерфейсом, ответственным за прием команд из внешних источников
        :param args: tuple
        :param kwargs: dict
        :return: mixed
        """
        self.bus.publish("on_execute_command", *args, **kwargs)
        # преобразуем командную строку в массив

        module_name, namespace, cmd = self.get_task_data(kwargs['api.cmd'], kwargs.get('api.namespace', None))

        instance = self.instantiate_module(module_name, namespace)

        # команды мы различаем по префиксу cmd_ перед самим названием команды.
        cmd = "cmd_%s" % cmd

        cmd_info = self.check_command_exists(instance, cmd)

        cmd_args = self.check_command_args(instance, cmd, cmd_info, kwargs)

        if self.is_method_exists(instance, "before_command"):
            if not self.call_method(instance, "before_command", cmd):
                raise exception.BadRequestError(
                    "before command returned False, None, or equivalent value. Command execution terminated")

        self.bus.publish("on_before_command", cmd, **cmd_args)

        task = self.wrap_task(task_id, instance, cmd, *args, **cmd_args)

        result = task.run()

        # result = self.call_method(instance, cmd, **cmd_args)

        if self.is_method_exists(instance, "after_command"):
            self.bus.publish("on_after_command", cmd=cmd, result=result)
            self.call_method(instance, "after_command", cmd, result)

        del instance
        del task
        return result


