__author__ = 'nolka'

import os
import re
from collections import OrderedDict

from system.platforms.services import BaseServicePlatform
from system.lib.tools import random_str


class Samp(BaseServicePlatform):
    def __init__(self, host_server, attributes):
        BaseServicePlatform.__init__(self, host_server, attributes)

        # service-specific parameters for current account
        if "service_config" in attributes.keys():
            self.service_config = attributes["service_config"]
        else:
            self.service_config = dict()

        self.configs = os.path.join(self.service_root, "server.cfg")
        self.executable_name = "samp03svr"


    def open(self, config_name):
        if self.parsed_config is None:
            self.parsed_config = OrderedDict()
        handle = open(config_name, 'r')
        r = re.compile("\s+")
        for line in handle:
            line = line.strip()
            param, value = r.split(line, 1)
            self.logger.debug("  parsed %s = %s" % (param, value))
            self.parsed_config[param] = value
        handle.close()
        self.logger.debug("Config parsed sucessfully")

    def save(self, config_name):
        self.logger.debug("Saving config file...")
        temp_config_name = "/tmp/samp_%s.tmp" % random_str()
        handle = open(temp_config_name, 'w')
        for k, v in self.parsed_config.items():
            handle.write("%s %s\n" % (k, v))
        handle.close()
        self.host_server.cp(temp_config_name, self.configs, self._get_user_name())

    def get_slot_count(self):
        return self.parsed_config['maxplayers']

    def get_port(self):
        return int(self.parsed_config['port'])

    def set_port(self, value):
        self.parsed_config['port'] = value

    def set_slot_count(self, value):
        self.parsed_config['maxplayers'] = value

    def get(self, value):
        return self.parsed_config[value]

    def set(self, name, value):
        self.parsed_config[name] = value

    def sync_config(self):
        self.logger.info("Synchronizing configs...")
        self.open(self.configs)
        need_save = False
        if self.get("rcon_password") == "changeme":
            self.set("rcon_password", random_str(10))
            need_save = True
        for sparam, sval in self.service_config.items():
            if self.parsed_config[sparam] != sval:
                self.logger.warn(
                    "Config mismatch for [%s]. expected %s, got %s" % (sparam, sval, self.parsed_config[sparam]))
                self.parsed_config[sparam] = sval
                need_save = True

        if self.get_port() != int(self.service_info['port']):
            self.logger.warn('Port mismatch. expected "%s", got "%s"' % (self.service_info['port'], self.get_port()))
            self.parsed_config["port"] = self.service_info["port"]
            need_save = True

        if need_save:
            self.save(self.configs)


    def after_install(self):
        self.logger.debug("Configuring SAMP...")
        self.sync_config()
        self.response_data["rcon"] = self.parsed_config["rcon_password"]




