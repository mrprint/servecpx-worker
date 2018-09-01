
import os
import sys
import pika
import re

from model import LogFileModel
from system.lib import VarExpander
from system.queue import connect_mq, declare_channel
from system.logger import Logger
from system.runnable.default_worker.cmdline import QueueListenerParams
from system.runnable import BaseRunnable
import options


class Emitter(BaseRunnable):

    def __init__(self, cmdline_options, logger):
        super(Emitter, self).__init__(cmdline_options, logger)
        self._logfiles = {}
        self._received_messages = 0

    @staticmethod
    def get_cmdline_parser():
        return QueueListenerParams()

    @classmethod
    def get_logger(cls):
        return Logger(cls.__name__, log_to_file=False)

    def filter_message(self, message_line):
        m = LogFileModel.parse(message_line)
        if m.exists():
            return m
        raise IOError("Log file: %s was not found" % m.file_name)

    def register_logfile(self, model):
        """

        :param model:
        :type model: LogFileModel
        :return:
        """
        if model.file_name not in self._logfiles.keys():
            self._logfiles[model.file_name] = model

    def log_names_receiver(self, channel, method, properties, body):
        """

        :param channel:
        :type channel: pika.adapters.blocking_connection.BlockingChannel
        :param method:
        :param properties:
        :param body:
        :return:
        """

        if self._received_messages % 1000 == 0:
            self.logger.debug("Received: %s" % body)
        try:
            model = self.filter_message(body)
            self.register_logfile(model)
        except IOError as e:
            self.logger.error("Failed to listen logfile %s" % e)

        channel.basic_ack(delivery_tag=method.delivery_tag)
        self._received_messages += 1

        self.save_files_list(self._logfiles)

        channel.basic_publish(self.options.exchange,
                              self.options.route,
                              re.sub("\[\d+\]", "[%d]" % self._received_messages, body)
                          )

    def save_files_list(self, file_list):
        with open("/tmp/files_to_log", "w") as f:
            for fn, model in file_list.iteritems():
                f.write("%s\n" % model)

    def run(self):
        self.logger.info('Privetik!')
        conn = connect_mq(self.options.host,  pika.PlainCredentials(options.queue_login, options.queue_password))
        chan = declare_channel(conn, self.options.exchange, self.options.queue,
                               self.options.route,
                               'topic')
        chan.basic_qos(prefetch_count=1)
        try:
            chan.basic_consume(self.log_names_receiver, queue=self.options.queue)
            chan.start_consuming()
        except KeyboardInterrupt:
            self.logger.warn("Exiting...")
            chan.close()
            conn.close()
            self.logger.warn("Transport successfully closed.")
            self.save_files_list(self._logfiles)
            self.logger.info("File list saved.")
