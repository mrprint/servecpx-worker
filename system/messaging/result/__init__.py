import datetime

from system.messaging import Serializable


class TaskResult(Serializable):
    def __init__(self, task_id, response={}):
        self.type = 'task'
        self.task_id = task_id
        self.response = response


class ActionResult(Serializable):
    def __init__(self, action_name, response={}):
        self.type = 'action'
        self.action_name = action_name
        self.data = response
