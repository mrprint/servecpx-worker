__author__ = 'nolka'

import os
import sys

from system.lib import VarExpander
from system.logger import Logger
from cmdline import WorkerServiceInstallerParams
from system.paramsparser.base import ModuleRunParams
from system.runnable import BaseRunnable
import options


_service_root = {
    "systemd": "/etc/systemd/system",
    "upstart": "/etc/init/"
}

_filename_template = {
    "systemd": "%s.service",
    "upstart": "%s.conf"
}


class Installer(BaseRunnable):
    def __init__(self, cmdline_options, *args, **kwargs):
        if not os.getuid() == 0:
            sys.exit("Installer must be started with root privileges!")

        BaseRunnable.__init__(self, cmdline_options, *args, **kwargs)

    @staticmethod
    def get_cmdline_parser():
        return WorkerServiceInstallerParams()

    @classmethod
    def get_logger(cls):
        return Logger(cls.__name__, log_to_file=True)

    def install(self):
        template_file = os.path.join(options.ROOT, self.options.template)
        if not os.path.exists(template_file):
            raise Exception("Template file %s was not found!" % template_file)
        self.logger.info("Using service template %s" % template_file)
        dest_file_path = _service_root[self.options.initializer]
        dest_file_name = os.path.join(dest_file_path, "%s.service" % self.options.service_name)

        if os.path.exists(dest_file_name):
            self.logger.fatal("Service with same name already installed: %s" % dest_file_name)
            return False

        self.logger.info("Installing template to: %s" % dest_file_name)

        module_run_params = ModuleRunParams()

        ve = VarExpander(self.options.dict())
        ve.add_vars(module_run_params.dict())
        with open(template_file, 'r') as f:
            with open(dest_file_name, 'w') as sf:

                compiled = ve.expand(f.read(), False)

                if self.options.dump_template:
                    self.logger.debug(compiled)

                sf.write(compiled)
                self.logger.info("Template successfully installed!")

    def uninstall(self):
        service_name = os.path.join(_service_root[self.options.initializer], "%s.service" % self.options.service_name)
        if not os.path.exists(service_name):
            self.logger.fatal('File does not exists: %s' % service_name)
            return False
        self.logger.info('Removing file: %s' % service_name)
        os.unlink(service_name)
        self.logger.info('Done!')

    def run(self):
        if self.options.action == 'install':
            self.install()
        elif self.options.action == 'uninstall':
            self.uninstall()


