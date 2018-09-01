__author__ = 'nolka'

import argparse


class BaseParams(object):
    def dict(self):
        return vars(self)


class ModuleRunParams(BaseParams):
    def __init__(self):
        m = argparse.ArgumentParser(description="Core parameters parser %(prog)s")
        m.add_argument(
            '--handler',
            type=str,
            default='default_worker.QueueListener',
            action="store",
            help='A class to handle queue messages'
        ),
        m.add_argument(
            '--mode',
            type=str,
            default="production",
            action="store",
            help="Define running mode for worker"
        )
        self.__dict__.update(vars(m.parse_known_args()[0]))