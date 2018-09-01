# -*- coding: utf8 -*-
__author__ = 'nolka'

import pika
import simplejson

import options


def connect_mq(host, credentials=None):
    params = dict(host=host, heartbeat_interval=30)
    if credentials is not None:
        params['credentials'] = credentials
    conn = pika.BlockingConnection(pika.ConnectionParameters(**params))
    return conn


def declare_channel(connection, exchange, queue, route, exchange_type='topic'):
    """

    :param connection:
    :type connection: pika.adapters.blocking_connection.BlockingConnection
    :param exchange:
    :type exchange: str
    :param queue:
    :type queue: str
    :param route:
    :type route: str
    :param exchange_type:
    :type exchange_type: str
    :return:
    """
    chan = connection.channel()
    chan.exchange_declare(exchange, durable=True, type=exchange_type)
    queue_info = chan.queue_declare(queue=queue, exclusive=False, durable=True)
    chan.queue_bind(queue=queue, exchange=exchange, routing_key=route)
    return chan


class RabbitQueue(object):

    def __init__(self, host='localhost', exchange=None, route=None, queue=None, type='direct', raw_messages=False, logger=None):
        self.host = host
        self.exchange = exchange
        self.route = route
        self.queue = queue
        self.type = type
        self.raw_messages = raw_messages

        self.logger = logger

        cred = pika.PlainCredentials(options.queue_login, options.queue_password)
        self.conn = pika.BlockingConnection(pika.ConnectionParameters(
            host=self.host,
            credentials=cred,
            heartbeat_interval=30
        ))

        self.logger.debug("created connection")

        self.chan = self.conn.channel()
        if self.exchange is not None:
            self.chan.exchange_declare(
                exchange=self.exchange,
                durable=True,
                type=self.type
            )
            self.logger.debug("exchange declared")

        if self.queue is None:
            queue_info = self.chan.queue_declare(
                exclusive=True,
                durable=False
            )
            self.queue = queue_info.method.queue
        else:
            self.chan.queue_declare(queue=self.queue, durable=True)
            self.logger.debug("queue created")

        if self.exchange is not None and self.route is None:
            self.logger.debug("bind queue %s to exchange %s" % (self.queue, self.exchange))
            self.chan.queue_bind(exchange=self.exchange, queue=self.queue)
        elif self.exchange is not None and self.route is not None:
            self.logger.debug("bind queue %s to exchange %s with route %s" % (self.queue, self.exchange, self.route))
            self.chan.queue_bind(exchange=self.exchange, routing_key=self.route, queue=self.queue)
        elif not any(self.exchange, self.route):
            self.logger.debug("no exchange  and route specified!")

        self.logger.debug("init complete")


class Producer(RabbitQueue):

    def send(self, message, code=0, metadata=None, route=None):
        body = {
            "code": code,
            "data": message
        }

        if isinstance(metadata, dict):
            body['metadata'] = metadata

        params = {
            "exchange": self.exchange,
            "properties": pika.BasicProperties(
                delivery_mode=2,
            )
        }

        if self.raw_messages:
            params.update({
                "body": message
            })
        else:
            params.update({
                "body": simplejson.dumps(body)
            })

        if self.route is not None and route is not None:
            params.update({
                "routing_key": route,
            })
        else:
            params.update({
                "routing_key": self.route,
            })

        self.logger.debug("sending->%s[%s]:%s/%s/%s: %s" % (
            str(self.host),
            str(self.type),
            str(self.exchange),
            str(params['routing_key']),
            str(self.queue),
            message
        ))

        self.chan.basic_publish(
            **params
        )


class Listener(RabbitQueue):
    def fetch(self, callback):
        self.chan.basic_qos(prefetch_count=1)
        self.chan.basic_consume(callback, queue=self.queue)
        self.chan.start_consuming()










