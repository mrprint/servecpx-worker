# -*- coding: utf8

import jsonpickle
import jsonpickle.handlers

import time
import datetime

import decimal


class DictHandler(jsonpickle.handlers.BaseHandler):   
    def flatten(self, obj, data):
        r = {}
        for k in obj:
            value = obj[k]
            if isinstance(value, int):
                r[k] = int(value)
            elif isinstance(value, float):
                r[k] = float(value)
            elif isinstance(value, bool):
                r[k] = bool(value)
            elif isinstance(value, datetime.datetime):
                r[k] = value.strftime("%Y-%m-%d %H:%M:%S")#'/Date(%d+0800)/' % time.mktime(value.timetuple())
            elif isinstance(value, dict):
                r[k] = self.flatten(self.value, data)
            elif value is None:
                r[k] = None
            else:
                r[k] = str(value);
        return r
    
class DecimalHandler(jsonpickle.handlers.BaseHandler):    
    def flatten(self, obj, data):
        return str(obj)

class DatetimeHandler(jsonpickle.handlers.BaseHandler):    
    def flatten(self, obj, data):
        return '/Date(%d+0800)/' % time.mktime(obj.timetuple())