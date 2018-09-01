__author__ = 'nolka'

import re

from system.platforms.os import OsPlatform
import options as config


class BasicPidStatsCollector(object):
    def __init__(self, pids):
        self.pids = pids

    def read(self):
        h = OsPlatform(config.host_os_service_initializer)
        r, data, err = h.execute("""ps -p %(pids)s -o pid,rss,pcpu --no-headers""" % {
            "pids": ",".join([str(x) for x in self.pids]),
        })
        return data

class ServicePidStatsCollector(BasicPidStatsCollector):
    def __init__(self, service_pid):
        self.service_pid = service_pid
        super(ServicePidStatsCollector, self).__init__([x[1] for x in self.service_pid])


class BasicPidStatsParser(object):
    def __init__(self, pids_collector):
        self._collector = pids_collector
        self.data = {}

    def build_pid_map(self):
        for pid in self._collector.pids:
            self.data[pid] = None

    def parse(self):
        stats = self._collector.read()

        self.build_pid_map()

        rex = re.compile("[\t\s]+")
        for stat_line in stats.strip(" \t\n\r").split("\n"):
            pid, mem, cpu = rex.split(stat_line.strip(" \t\n\r"))
            self.data[pid] = dict(cpu_avg=int(float(cpu) * 100), ram=mem)

        return self.data

class ServicePidStatsParser(BasicPidStatsParser):
    def build_pid_map(self):
        for svc_id, pid in self._collector.pids:
            self.data[svc_id] = None

    def parse(self):
        stats = self._collector.read()
        self.build_pid_map()

        rex = re.compile("[\t\s]+")

class ServicePidBinder(object):
    def __init__(self, parser):
        self.parser = parser

    def bind(self):
        pidmap = self.parser.parse()