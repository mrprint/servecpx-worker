from model import Serializable
from datetime import datetime


class BaseResponse(Serializable):
    def __init__(self, result={}, status_code=0, **kwargs):
        self.data = result
        self.code = status_code

        self.__dict__.update(kwargs)


class ErrorResponse(Serializable):
    def __init__(self, status_code=-1, job={}, message=None, trace=None, custom_data=None,
                 date_time=datetime.today().strftime("%Y-%m-%d %H:%M:%S"), **kwargs):
        self.code = status_code
        self.data = {
            "message": message,
            "trace": trace,
            "job": job,
            "custom_data": custom_data,
            "worker_time": date_time,
        }

        self.__dict__.update(kwargs)
