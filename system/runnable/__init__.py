# -*- coding: utf8
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
import options


class BaseRunnable(object):
    def __init__(self, cmdline_options, logger):
        self.options = cmdline_options
        self.logger = logger
        self.logger.info("Initialized")

    def run(self):
        raise NotImplementedError("runnable is not implemented in " + self.__class__.__name__)

    @staticmethod
    def get_cmdline_parser():
        raise NotImplementedError()

    @classmethod
    def get_logger(cls, file_name='general_log'):
        return Logger(cls.__name__, file_name=file_name)

class LogListenerHandler(BaseRunnable):
    def __init__(self):
        pass

class FakeWorker(BaseRunnable):

    def handle(self, channel, method, properties, body):
        self.logger.info("RECV: %s" % body)
        channel.basic_ack(delivery_tag=method.delivery_tag)