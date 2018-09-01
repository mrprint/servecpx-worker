__author__ = 'nolka'

import os
from multiprocessing import Queue
from multiprocessing import Process


class FileWatcher(object):
    def __init__(self, file_list, new_files_queue, log_records_queue):
        self.file_list = file_list
        self.new_files_queue = new_files_queue
        self.log_records_queue = log_records_queue

    def watch(self):
        pass
