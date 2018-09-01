__author__ = 'nolka'

import traceback

from system.messaging.model import Serializable
from system.task import SimpleTask

from system.lib.decorators import before_after

from system.runnable import BaseRunnable

from system.messaging.model import ResourceUsage
from system.messaging.result import TaskResult

from system.messaging import BaseResponse, ErrorResponse


class SomeJobClass(Serializable):
    def run_method_with_error(self, arg, kw=None):
        print arg+kw

    def run_normal(self, a,b):
        return a+b

class Main(BaseRunnable):
    @staticmethod
    def get_cmdline_parser():
        return None

    @classmethod
    def get_logger(cls):
        return super(Main, cls).get_logger(file_name='test_runnable')

    def before(self):
        self.logger.info("Before func")

    def after(self):
        self.logger.info("After func")

    @before_after(before=before, after=after)
    def run(self):
        print "test_handle"

        # r = ResourceUsage(ram=2, cpu_avg=5)
        # r.add_service_report(123, 23, 43)

        # task = TaskResult(1, r)
        # er = ErrorResponse(500, task, "error_msg", "azaza", 'trace')

        job = SomeJobClass()
        task = SimpleTask(-1, job, 'run_normal', 1, 2)
        try:
            result = task.run()
            task_result = TaskResult(task.id, result)
            r = BaseResponse(task_result)
        except Exception as e:
            r = ErrorResponse(500, task, "%s" % e, traceback.format_exc())

        # br = BaseResponse(r)
        print r
        # print br
        # print er
