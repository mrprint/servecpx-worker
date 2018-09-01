__author__ = 'nolka'

import argparse
from workerparams import QueueListenerParams


class WorkerServiceInstallerParams(QueueListenerParams):
    def __init__(self):
        super(self.__class__, self).__init__()
        m = argparse.ArgumentParser(description="Worker service installer args %(prog)s")
        m.add_argument(
            '--template', '-T',
            default='docs/templates/worker-systemd-service.template',
            help='Template name which used to install'
        )
        m.add_argument(
            '--initializer', '-I',
            default='systemd',
            help='System services initializer'
        )
        m.add_argument(
            '--runnable', '-R',
            default="default_worker.QueueListener",
            help='Which module to be used to run as service'
        )
        m.add_argument(
            '--service-name', '-S',
            default="gamecp-worker",
            dest='service_name',
            help='Which service name to be used',
        )
        m.add_argument(
            '--action', '-A',
            default='install',
            choices=('install', 'uninstall'),
            help='Action to execute'
        )
        m.add_argument(
            '--dump-template', '-D',
            dest='dump_template',
            action='store_const',
            const=True,
        )
        self.__dict__.update(vars(m.parse_known_args()[0]))
