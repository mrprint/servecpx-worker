__author__ = 'nolka'

import os

from system.platforms.services import BaseServicePlatform
from system.lib.tools import random_str
from system.platforms.services.configparsers import MinecraftConfig


class Minecraft(BaseServicePlatform):
    def __init__(self, host_server, attributes):
        BaseServicePlatform.__init__(self, host_server, attributes)

        # service-specific parameters for current account
        if "service_config" in attributes.keys():
            self.service_config = attributes["service_config"]
        else:
            self.service_config = dict()

        self.config_name = os.path.join(self.service_root, "server.properties")

    def sync_config(self):
        self.logger.info("Synchronizing configs...")
        mc = MinecraftConfig(self.config_name)
        mc.open()

        need_save = False
        if mc.get("rcon.password") is None:
            mc.set("rcon.password", random_str(10))
            self.response_data["rcon"] = mc.get("rcon.password")
            need_save = True
        for sparam, sval in self.service_config.items():
            if mc.get(sparam) != sval:
                self.logger.warn(
                    "Config mismatch for [%s]. expected %s, got %s" % (sparam, sval, mc.get(sparam)))
                mc.set(sparam, sval)
                need_save = True

        if mc.get('server-port', int) != int(self.service_info['port']):
            self.logger.warn(
                'Port mismatch. expected "%s", got "%s"' % (self.service_info['port'], mc.get('server-port')))
            mc.set('server-port', self.service_info["port"])
            mc.set('rcon.port', mc.get("server-port", int) + 1001)
            need_save = True

        if mc.get('eula') is None:
            mc.set('motd', 'GameCP service hosting for minecraft. http://nolka.ru')
            mc.set('snooper-enabled', 'false')
            mc.set('eula', 'true')
            need_save = True

        if need_save:
            mc.save()
            self.host_server.execute(
                "chown %(user_name)s:%(user_name)s %(file_name)s" % dict(user_name=self._get_user_name(),
                                                                         file_name=self.config_name))

    def after_install(self):
        self.logger.debug("Configuring minecraft instance...")
        with open("eula.txt", "w") as f:
            f.write("eula=true")
        self.host_server.execute(
            "chown %(user_name)s:%(user_name)s eula.txt" % dict(user_name=self.user_info['nick_name']))
        self.sync_config()




