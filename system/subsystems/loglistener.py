__author__ = 'nolka'

import pika
import config

class LogListener(object):
    def __init__(self, account_id, service_id, path_to_logfile, **kwargs):
        self.account_id = account_id
        self.service_id = service_id
        self.path_to_logfile = path_to_logfile
        self.logfile = open(path_to_logfile, "r")
        cred = pika.PlainCredentials(config.que_login, config.que_password)
        self.conn = pika.BlockingConnection(pika.ConnectionParameters(
            host=self.host,
            credentials=cred,
        ))

    def close(self):
        try:
            self.logfile.close()
        except:
            self.logger.error("Failed to close logfile: %s" % self.path_to_logfile)

