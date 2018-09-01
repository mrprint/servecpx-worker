# -*- coding: utf8

class RequestException(Exception):
    code = 500

class BadRequestError(RequestException):
    code = 400

class AccessDeniedError(RequestException):
    code = 403

class InvalidApplicationError(RequestException):
    code = 405

class NotImplementedError(RequestException):
    code = 501
    
class InternalError(RequestException):
    pass

class NotFoundError(RequestException):
    code = 404

class NoTasksFoundError(NotFoundError):
    pass

class NoProxyFoundError(NotFoundError):
	pass

class ShellCommandError(RequestException):
    def __init__(self, message, cmd_code, stdout, stderr):
        super(ShellCommandError, self).__init__("%s: stderr: %s. stdout: %s" % (message, stderr, stdout))
        self.code = cmd_code
        self.custom_data = dict(
            stdout=stdout,
            stderr=stderr
        )
class AlreadyRunningError(RequestException):
    code=200