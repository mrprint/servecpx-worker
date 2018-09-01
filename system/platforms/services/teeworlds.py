__author__ = 'nolka'

import re
from collections import OrderedDict

from system.platforms.services import BaseServicePlatform
from system.lib.tools import random_str


class Teeworlds(BaseServicePlatform):
    def __init__(self, host_server, attributes):
        BaseServicePlatform.__init__(self, host_server, attributes)

        if "service_config" in attributes.keys():
            self.service_config = attributes["service_config"]

        self.configs = os.path.join(self.service_root, "server.cfg")
        self.executable_name = "teeworlds_srv"

    def open(self, config_name):
        if self.parsed_config is None:
            self.parsed_config = OrderedDict()
        try:
            handle = open(config_name, 'r')
            r = re.compile("\s+")
            for line in handle:
                line = line.strip()
                param, value = r.split(line, 1)
                self.logger.debug("  parsed %s = %s" % (param, value))
                self.parsed_config[param] = value
            handle.close()
            self.logger.debug("Config parsed sucessfully")
        except:
            self.logger.error("Config file was not found.")

    def save(self, config_name):
        self.logger.debug("Saving config file...")
        temp_config_name = "/tmp/teeworlds_%s.tmp" % random_str()
        handle = open(temp_config_name, 'w')
        for k, v in self.parsed_config.items():
            handle.write("%s %s\n" % (k, v))
        handle.close()
        self.host_server.cp(temp_config_name, self.configs, self._get_user_name())

    def get_slot_count(self):
        return self.parsed_config.get('sv_max_clients', -1)

    def get_port(self):
        return int(self.parsed_config.get('sv_port', -1))

    def setPort(self, value):
        self.parsed_config['sv_port'] = value

    def set_slot_count(self, value):
        self.parsed_config['sv_max_clients'] = value

    def get(self, value):
        return self.parsed_config.get(value, None)

    def set(self, name, value):
        self.parsed_config[name] = value

    def sync_config(self):
        self.logger.info("Synchronizing configs...")
        self.open(self.configs)
        need_save = False
        if self.get("sv_rcon_password") is None:
            self.set("sv_rcon_password", random_str(10))
            need_save = True

        if self.get("sv_bindaddr") != self.service_info["address"]:
            self.set("sv_bindaddr", self.service_info["address"])
            need_save = True

        for sparam, sval in self.service_config.items():
            if self.parsed_config.get(sparam, None) != sval:
                self.logger.warn(
                    "Config mismatch for [%s]. expected %s, got %s" % (sparam, sval, self.get(sparam)))
                self.parsed_config[sparam] = sval
                need_save = True

        if self.get_port() != int(self.service_info['port']):
            self.logger.warn('Port mismatch. expected "%s", got "%s"' % (self.service_info['port'], self.get_port()))
            self.setPort(self.service_info["port"])
            need_save = True

        if need_save:
            self.save(self.configs)

    def after_install(self):
        self.logger.debug("Configuring teeworlds instance...")
        self.syncConfig()
        self.response_data['rcon'] = self.parsed_config["sv_rcon_password"]




