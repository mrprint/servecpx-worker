# -*- coding: utf8

import sys
import re

import datetime
from system.platforms.os import OsPlatform
from system.basemodule import BaseModule
import options as config


class Maintenance(BaseModule):
    def cmd_ping(self):
        return "pong"

    def cmd_getHostStats(self, attributes):
        h = OsPlatform(config.host_os_service_initializer)
        resp = {
            "date_created": datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
            "ram": 0
        }
        r, usage, err = h.execute("""cat /proc/loadavg| awk '{print $1*100}'""")

        if "check_services" in attributes.keys():
            rex = re.compile("[\t\s]+")
            pidstats = dict([(x[0], dict(pid=x[1])) for x in attributes["check_services"]])

            for svcid, svcdata in pidstats.items():
                data = None
                try:
                    r, data, err = h.execute("""ps -p %(pids)s -o pid,rss,pcpu --no-headers""" % {
                        "pids": svcdata["pid"],
                    })
                except:
                    pass

                if data:
                    pid, mem, cpu = rex.split(data.strip(" \t\n\r"))
                    pidstats[svcid] = dict(cpu_avg=int(float(cpu) * 100), ram=mem)
                else:
                    pidstats[svcid] = None

            resp["services_report"] = pidstats

        resp["cpu_avg"] = int(usage.strip())

        return resp

    def cmd_changeUserPassword(self, user, password):
        h = OsPlatform(config.host_os_service_initializer)
        h.execute("""echo '%(user)s:%(password)s' | chpasswd""" % {
            "user": "%s%s" % (user, config.user_name_suffix),
            "password": password
        })

        return True


    def cmd_reboot(self, reason=None):
        if reason:
            self.logger.warn("Rebooting with reason: %s" % reason)
        sys.exit(0)