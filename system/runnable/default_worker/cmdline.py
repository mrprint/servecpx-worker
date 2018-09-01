__author__ = 'nolka'

import argparse
from system.paramsparser.base import BaseParams


class QueueListenerParams(BaseParams):
    def __init__(self):
        m = argparse.ArgumentParser(description="Work manager for gamecp %(prog)s")
        m.add_argument(
            '--host', '-H',
            type=str,
            required=True,
            action="store",
            help='queue messaging server host'
        )
        m.add_argument(
            '--my_ip', '-M',
            type=str,
            default='localhost',
            action="store",
            help='worker host ip (used in queue name and route generation)'
        )
        m.add_argument(
            '--type', '-T',
            type=str,
            default='direct',
            action="store",
            help='exchange point type. default: direct'
        )
        m.add_argument(
            '--exchange', '-E',
            type=str,
            default='local',
            action="store",
            help='queue exchange point'
        )
        m.add_argument(
            '--route', '-R',
            type=str,
            default=None,
            action="store",
            help='queue route'
        )
        m.add_argument(
            '--queue', '-Q',
            type=str,
            default=None,
            action=None,
            help='queue name'
        )
        m.add_argument(
            '--err_host',
            type=str,
            default='localhost',
            action="store",
            help='errors queue messaging server host'
        )
        m.add_argument(
            '--err_exchange',
            type=str,
            default='local_err',
            action="store",
            help='errors queue exchange point'
        )
        m.add_argument(
            '--err_route',
            type=str,
            default=None,
            action="store",
            help='errors queue route'
        )
        m.add_argument(
            '--err_queue',
            type=str,
            default='',
            action="store",
            help='errors queue name'
        )

        self.__dict__.update(vars(m.parse_known_args()[0]))