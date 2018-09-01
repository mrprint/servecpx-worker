import simplejson

from datetime import datetime


class Serializable(object):
    def __str__(self):
        return simplejson.dumps(vars(self), default=lambda x: vars(x))


class ResourceUsage(Serializable):
    def __init__(self, ram=0, cpu_avg=0, date_created=datetime.today().strftime("%Y-%m-%d %H:%M:%S")):
        self.date_created = date_created
        self.ram = ram
        self.cpu_avg = cpu_avg
        self.services_report = {}

    def add_service_report(self, service_id, ram, cpu_avg):
        self.services_report.update({
            service_id: {
                'ram': ram,
                'cpu_avg': cpu_avg
            }
        })
