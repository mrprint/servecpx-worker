from system.runner import BaseRunnable

import logging

class Main(BaseRunnable):
    @staticmethod
    def get_cmdline_parser():
        return None

    @classmethod
    def get_logger(cls):
        logger = logging.getLogger(cls.__name__)
        logger.setLevel(logging.DEBUG)

        stream_handler = logging.StreamHandler()

        logger.addHandler(stream_handler)
        return logger

    def run(self):
        self.logger.info("Test runnable started and exited :D")
