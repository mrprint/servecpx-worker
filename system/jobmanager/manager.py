__author__ = 'nolka'

import time
import traceback
from multiprocessing import Queue, Process, Manager
import pprint

from task import SimpleTask, BaseTask


class JobManager(object):
    def __init__(self, result_handler=None, logger=None):
        self.result_handler = result_handler
        self.logger = logger
        self.running_workers = 0
        self._counter = 0
        self.jobs_added = 0
        self.jobs_completed = 0

        self._manager = Manager()

        self.jobs_queue = None
        self.results_queue = self._manager.Queue()

        self.results_handler = None
        self.workers = []
        self.logger.info("JobManager initialized")

    def add_workers(self, worker_type, count=1):
        if not self.workers:
            self.jobs_queue = self._manager.Queue(count)

        for _id in xrange(count):
            self._configure(worker_type)

    def _configure(self, type_name, name=None):
        instance = type_name(self.jobs_queue, self.results_queue)
        instance.name = unicode(name) if name else u"<{} worker {}>".format(type(instance).__name__, len(self.workers))

        self.workers.append(instance)
        self.logger.debug("Created worker %s in thread %d" % (instance.name, id(instance)))

    def do_work(self):
        for w in self.workers:
            self.logger.debug("Starting worker {}".format(w.name))
            w.start()
            self.running_workers += 1

        self.logger.debug('Starting results listener thread')
        self.result_handler = Process(target=self.result_handler, args=(self, self.results_queue))
        self.result_handler.start()
        self.logger.debug('Startup completed.')

    def add_job(self, task, task_id=None, task_wrapper=SimpleTask):
        if task_id is None:
            task_id = self.jobs_added

        if task is None:
            self.logger.warn("Sending poison task...")
            self.jobs_queue.put(None)
        if isinstance(task, BaseTask):
            if not task.id:
                task.set_id(task_id)
                print(task)
            self.jobs_queue.put(task)
        else:
            self.jobs_queue.put(task_wrapper(task_id, data=task))
        self.logger.debug('New job added to queue. Counter is {}'.format(self.jobs_added))
        self.jobs_added += 1

    def exit(self, wait_until_exit=True):
        self.logger.debug("Started workers count %d" % self.running_workers)
        for i in xrange(self.running_workers):
            self.jobs_queue.put(None)

        self.logger.debug("Joining worker threads...")
        self.jobs_queue.close()
        self.jobs_queue.join_thread()

        if wait_until_exit:
            for _id, w in enumerate(self.workers):
                self.logger.debug("Joining thread %s..." % w.name)
                self.workers[_id].stop()
                self.running_workers -= 1

        self.logger.debug("Joining results_queue thread...")
        self.results_queue.put(None)
        self.result_handler.join()
        self.results_queue.close()
        self.results_queue.join_thread()

        if wait_until_exit:
            self.logger.debug("Waiting worker threads for exit...")
            _alive_threads = True
            while _alive_threads:
                for w in self.workers:
                    if w.is_alive():
                        _alive_threads = True
                    else:
                        _alive_threads = False
                if _alive_threads or self.result_handler.is_alive():
                    self.logger.warn("waiting...")
                    time.sleep(.1)
                else:
                    break
