#!/usr/bin/python
__author__ = 'nolka'

import subprocess

from system.runnable.default_worker.workerparams import QueueListenerParams
from system.queue import Producer


def main():
    options = QueueListenerParams().options
    manager = Producer(
        'localhost',
        exchange=options.exchange,
        route=options.route,
        queue=options.queue,
        type=options.type,
        raw_messages=True
    )

    p = subprocess.Popen(['tail', '-f', '/var/log/syslog'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        line = p.stdout.readline()
        if "ovpn" in line:
            manager.send(line, route='openvpn')
        elif "CRON" in line:
            manager.send(line, route='cron')
        else:
            manager.send(line)


if __name__ == "__main__":
    main()