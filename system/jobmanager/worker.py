__author__ = 'nolka'

import logging
import traceback
from  multiprocessing.queues import Queue, Empty
from multiprocessing import Process

from task import BaseTask


class BaseWorker(Process):
    def __init__(self, jobs, results, name=None, manager=None, logger=None, target=None, args=(), kwargs={}):
        super(BaseWorker, self).__init__(target=target, args=args, kwargs=kwargs)

        self.name = unicode(name)
        self.manager = manager
        self.shutdown_pending = False
        self.logger = logger or logging
        self.results_queue = results
        self.jobs_queue = jobs


    def run(self):
        """

        :param jobs:
        :type jobs: Queue
        :param results:
        :type results: Queue
        :return:
        """
        while not self.shutdown_pending:
            try:
                # print "getting job!"
                task = self.jobs_queue.get()
                print task
                if task is None:
                    self.logger.warn("%s is exiting..." % self.name)
                    return

                try:
                    r = self.execute(task)
                    if issubclass(r.__class__, BaseTask):
                        task = r
                    else:
                        task.success(r)

                except Exception as e:
                    self.logger.error("{task:=^64}".format(task="Task id: {}".format(task.id)))
                    self.logger.error("Error occurred in thread %s: %s\n%s" % (self.name, e, traceback.format_exc()))
                    task.failed(getattr(e, 'code', -500), "\n".join((e, traceback.format_exc())))
                finally:
                    self.results_queue.put(task)
            except KeyboardInterrupt as e:
                self.logger.warn("Terminating worker by Ctrl+C")
                return None
            except Empty:
                pass
            except Exception as e:
                self.logger.fatal("{title:+^64}".format(title="Unhandled exception in worker thread"))
                self.logger.fatal("{exception:+^64}".format(exception=e))
                self.logger.fatal(traceback.format_exc())

    def execute(self, task):
        raise NotImplementedError("Not implemented!")

    # def start(self, jobs, results, *args, **kwargs):
        # self._thread_handle = Process(target=lambda j, r: self.start(j, r), name=self.name, args=(jobs, results))
        # self._thread_
        # handle.start()
        # self.jobs = jobs
        # self.results = results
        #
        # self.listen_tasks(jobs, results)

    def stop(self):
        self.shutdown_pending = True
        self.join()

        # def __call__(self, jobs, results, *args, **kwargs):
        #     return self.listen_tasks(jobs, results)
