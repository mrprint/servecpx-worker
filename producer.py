#!/usr/bin/python
__author__ = 'nolka'

from system.runnable.default_worker.workerparams import QueueListenerParams
from system.queue import Producer


def main():
    options = QueueListenerParams().options
    manager = Producer(
        host=options.host,
        exchange=options.exchange,
        route=options.route,
        queue=options.queue,
        type=options.type
    )

    manager.send(dict(cmd='Maintenance.ping',
                      recipient="xternalx@gmail.com",
                      subject="Test message topic",
                      message="Test message from queue"
    ), metadata = {
        'host': 'localhost',
        'exchange': 'site',
        'queue': 'tasks.done',
        'type': 'topic'
    })


if __name__ == "__main__":
    main()