# -*- coding: utf-8

import traceback
import time

import pika

import options
from queue import Listener

from system import handlers
from system.logger import Logger


class WorkManager():
    def __init__(self, options):
        self.options = options
        self.logger = Logger("WorkManager", "general_log")

    def getMessageSource(self):
        listener = Listener(
            host=self.options.host,
            exchange=self.options.exchange,
            route=self.options.route,
            queue=self.options.queue,
            type=self.options.type,
            logger=Logger("Listener")
        )

        return listener

    def doWork(self):
        worker_class = getattr(runnable, self.options.handler)
        while True:
            try:
                instance = worker_class(self.options, Logger(worker_class.__name__, file_name="general_log"))
                listener = self.getMessageSource()
                listener.fetch(instance.handle)
            except (pika.exceptions.ConnectionClosed, pika.exceptions.ConsumerCancelled) as e:
                self.logger.fatal("    !!>> Error: %s" % traceback.format_exc())
                self.logger.fata(
                    "Connection closed by server. Restarting worker in %d seconds..." % options.worker_restart_delay)
                time.sleep(options.worker_restart_delay)
            except pika.exceptions.AMQPConnectionError:
                self.logger.fatal("    !!>> Error: %s" % traceback.format_exc())
                self.logger.fatal(
                    "Some error occurred while try to connect to message broker. Restarting in %d seconds..." % options.worker_restart_delay)
                time.sleep(options.worker_restart_delay)
