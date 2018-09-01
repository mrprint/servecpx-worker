# -*- coding: utf-8
__author__ = 'nolka'

import os
import sys
import traceback
import time

import pika
import simplejson

from system.queue import Producer
from system.executer import Executer
from system import exceptions
from system.logger import Logger
from system.queue import Listener
from system.runnable import BaseRunnable
from cmdline import QueueListenerParams
import options


class ReplyTo(object):
    __slots__ = ['host', 'route', 'queue', 'type', '_route_str']

    def __init__(self, route_str):
        self._route_str = route_str
        parsed_data = dict(zip(('host', 'route', 'queue', 'type'), route_str.split("/")))
        for k, v in parsed_data.iteritems():
            setattr(self, k, v)

    def __eq__(self, other):
        if self.get_raw() == other.get_raw():
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_raw(self):
        return self._route_str


class QueueListener(BaseRunnable):

    def __init__(self, cmdline_options, *args, **kwargs):
        if not os.getuid() == 0:
            sys.exit("Worker instance must be started with root privileges!")

        BaseRunnable.__init__(self, cmdline_options, *args, **kwargs)
        self.pm = Executer(Logger("Executer"))
        self.pm.init_modules("common")

        self.producer = None

        self.last_reply_to = None

    @staticmethod
    def get_cmdline_parser():
        return QueueListenerParams()

    def send_result(self, reply_to, result, code=0):
        """
        Send response to specified queue
        :param reply_to: ReplyTo
        :param result: str
        :param code: int
        :return:
        """

        if not self.last_reply_to or self.last_reply_to != reply_to:
            self.last_reply_to = reply_to

            if hasattr(self.producer, "conn"):
                self.producer.conn.close()

            self.producer = Producer(
                host=reply_to.host,
                exchange=options.queue_exchange,
                route=reply_to.route,
                type=reply_to.type,
                queue=reply_to.queue,
                logger=Logger("Procuder")
            )

        self.producer.send(result, code)

    def get_message_source(self):
        listener = Listener(
            host=self.options.host,
            exchange=self.options.exchange,
            route=self.options.route,
            queue=self.options.queue,
            type=self.options.type,
            logger=Logger("Listener")
        )

        return listener

    def run(self):
        while True:
            try:
                listener = self.get_message_source()
                listener.fetch(self.do_work)
            except (pika.exceptions.ConnectionClosed, pika.exceptions.ConsumerCancelled) as e:
                self.logger.fatal("    !!>> Error: %s" % traceback.format_exc())
                self.logger.fatal(
                    "Connection closed by server. Restarting worker in %d seconds..." % options.worker_restart_delay)
                time.sleep(options.worker_restart_delay)
            except pika.exceptions.AMQPConnectionError:
                self.logger.fatal("    !!>> Error: %s" % traceback.format_exc())
                self.logger.fatal(
                    "Some error occurred while try to connect to message broker. Restarting in %d seconds..." % options.worker_restart_delay)
                time.sleep(options.worker_restart_delay)

    def do_work(self, channel, method, properties, body):
        self.logger.debug("Incoming workload: %s" % body)
        request = simplejson.loads(body)
        response = dict()
        response_code = 0
        try:
            if "task" in request.keys():
                self.task = request.get("task")
                if "command" not in self.task.keys():
                    raise exceptions.BadRequestError("No command specified!")

                data = {
                    "api.cmd": self.task.get("command"),
                    "api.namespace": "common"
                }

                if "command_data" in self.task.keys():
                    data.update(self.task.get("command_data"))

                self.pm.bus.publish("on_before_task", self.task)
                response['response'] = self.pm.execute(self.task.get('id'), **data)

            elif "execute_action" in request.keys():
                self.action = request.get("execute_action")
                if "cmd" not in self.action.keys():
                    raise exceptions.BadRequestError("No command specified!")

                self.pm.bus.publish("on_before_action", self.action)
                response['response'] = self.pm.execute(self.task.get('id'), **self.action)

            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:

            response_code = getattr(e, "code", -500)

            exc_info = sys.exc_info()
            exc_type, exc_value = exc_info[:2]

            # Формируем строку с трейсбеком
            trace_str = traceback.format_exc()

            self.logger.error("%s: %s\n%s" % (exc_type, exc_value, trace_str))
            response["message"] = "%s: %s" % (exc_type, exc_value)
            response["trace"] = trace_str
            response["custom_data"] = getattr(e, "custom_data", None)

            # Отмечаем сообщение как корректно обработанное, т.к. в случае, если его отметить необработанным, оно
            # появится в очереди вновь, таким образом мы получим зацикливание
            channel.basic_ack(delivery_tag=method.delivery_tag)
        finally:
            if getattr(self, "task", None):
                response["task_id"] = self.task.get("id")
                response["class"] = "task"
            if getattr(self, "action", None):
                response["action_name"] = self.action.get("cmd")
                response["class"] = "action"

            os.chdir(options.work_dir)

            message_route = properties.headers['X-ServeCP-ReplyTo']

            self.send_result(ReplyTo(message_route), response, response_code)
