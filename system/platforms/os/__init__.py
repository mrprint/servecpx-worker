# -*- coding: utf8
__author__ = 'nolka'

import os
import re

import options
from system.lib.tools import getLogger
from system.servers import HostServer
from system.exceptions import ShellCommandError
from system.lib import VarExpander


class TemplateCompiler(VarExpander):
    def getTemplateContent(self, script_name):
        with open(script_name) as h:
            return h.read()

    def compile(self, script_file, additional_attrs=dict()):
        self.add_vars(additional_attrs)
        tpl_text = self.getTemplateContent(script_file)
        return self.expand(tpl_text)


class OsPlatform(HostServer):
    def __init__(self, os_platform):
        super(OsPlatform, self).__init__()
        """ Calling parent constructor """

        self.os_platform = os_platform
        """ OS Platform name (upstart, systemd, etc...) """

        self.service_manager = None


    def expand(self, script, attributes):
        v = VarExpander(attributes)
        return v.expand(script)

    def compileTemplate(self, script_name, platform_alias, parameters, **kwargs):
        use_filename = None

        try_filenames = [
            [
                parameters.get("os_platform", options.host_os_service_initializer),
                parameters.get("mod_name", "std"),
                platform_alias,
                script_name
            ],
            [
                parameters.get("os_platform", options.host_os_service_initializer),
                parameters.get("mod_name", "std"),
                "_common",
                platform_alias,
                script_name
            ],
            [
                parameters.get("os_platform", options.host_os_service_initializer),
                "_common",
                parameters.get("mod_name", "std"),
                platform_alias,
                script_name
            ],
            [
                parameters.get("os_platform", options.host_os_service_initializer),
                "_common",
                script_name
            ],
            [
                "_common",
                script_name
            ]
        ]

        tc = TemplateCompiler(parameters)

        for filename in try_filenames:
            prefab = [options.ROOT, "config/scripts"] + list(filename)
            filename = "/".join(prefab)
            if os.path.exists(filename):
                use_filename = filename
                break
            else:
                self.logger.error("Script not found in: %s" % filename)

        if not use_filename:
            raise Exception("No service template are found or template is not a file!")

        self.logger.debug("Using template: %s" % use_filename)
        script = tc.compile(use_filename)
        return script

    def runScript(self, script_name, platform_alias, parameters, **kwargs):
        cmd_results = list()
        parameters.update(kwargs)

        script = self.compileTemplate(script_name, platform_alias, parameters, **kwargs)
        self.logger.debug("Compiled script looks like: %s" % script)
        for line in script.splitlines():
            r, stdout, stderr = self.execute(line)
            if not r:
                raise ShellCommandError(r, stdout, stderr)
            cmd_results.append(self.exec_result)

        if len(cmd_results) == 1:
            r = cmd_results[0]
            return r

        return cmd_results

    def getServiceManager(self, service_name, **kwargs):
        """
        @type service_name: str
        @rtype: BaseServiceManager
        """
        if not self.service_manager:
            klass = globals().get("%sManager" % self.os_platform.capitalize())
            self.service_manager = klass(self, service_name)
            for k, v in kwargs.iteritems():
                setattr(self.service_manager, k, v)

        """ Os-Specific service installer/uninstaller """
        return self.service_manager


class BaseServiceManager(object):
    def __init__(self, host_platform, service_name):
        """
        @type host_platform: OsPlatform
        @type service_name: str
        """
        self.logger = getLogger(type(self).__name__)
        self.host_platform = host_platform
        self.service_name = service_name

    def getPid(self, **kwargs):
        raise Exception("Method getPid is not implemented!")

    def install(self, content, **kwargs):
        self.logger.info("Installing service %s" % self.service_name)
        # self.logger.debug("Service content:\n%s" % content)
        filename = "%s%s%s" % (self.service_root, self.service_name, self.config_extension)
        with open(filename, "w") as f:
            f.write(content)
            f.close()

    def uninstall(self, **kwargs):
        filename = "rm %s%s%s" % (self.service_root, self.service_name, self.config_extension)
        self.logger.info("Uninstalling service with config: %s" % filename)
        self.host_platform.rm(filename)

    def start(self, **kwargs):
        raise Exception("Start method for service is not implemented!")

    def stop(self, **kwargs):
        raise Exception("Stop method for service is not implemented!")


class UpstartManager(BaseServiceManager):
    def __init__(self, host_platform, service_name):
        super(UpstartManager, self).__init__(host_platform, service_name)

        self.service_root = "/etc/init/"
        self.config_extension = ".conf"

    def getPid(self, text_for_search=None):
        if not text_for_search:
            r, text_for_search, stderr = self.host_platform.execute("/usr/sbin/service %s status" % self.service_name)
        print("Finding pid in text: %s" % text_for_search)
        r = re.compile("process\s+(?P<PID>\d+)$")
        pid = r.search(text_for_search).groupdict().get("PID", None)
        if pid is None:
            return -1
        self.logger.info("Requested pid is: %s" % pid)
        return int(pid)

    def start(self, **kwargs):
        try:
            self.host_platform.execute("/usr/sbin/service %s start" % self.service_name)
        except ShellCommandError as e:
            if "Job is already running" in e.message:
                return self.getPid(self.host_platform.exec_result.stdout)
        return self.getPid(self.host_platform.exec_result.stdout)

    def stop(self, **kwargs):
        try:
            self.host_platform.execute("/usr/sbin/service %s stop" % self.service_name)
        except ShellCommandError as e:
            handled = False
            non_fatal = [
                "Unknown instance",
                "unrecognized service"
            ]

            for part in non_fatal:
                if part in e.message:
                    handled = True

            if not handled:
                raise


class SystemdManager(BaseServiceManager):
    def __init__(self, host_platform, service_name):
        super(SystemdManager, self).__init__(host_platform, service_name)

        self.service_root = "/etc/systemd/system/"
        self.config_extension = ".service"

    def getPid(self):
        r, stdout, stderr = self.host_platform.execute("/bin/systemctl status %s.service" % self.service_name)
        r = re.compile("Main PID\: (?P<PID>\d+)")
        pid = r.search(stdout).groupdict().get("PID", None)
        if pid is None:
            return -1
        self.logger.info("Requested pid is: %s" % pid)
        return int(pid)

    def start(self, **kwargs):
        self.host_platform.execute("/bin/systemctl enable %s" % self.service_name)
        self.host_platform.execute("/bin/systemctl start %s.service" % self.service_name)
        if "service_info" in kwargs.keys():
            self.host_platform.execute(
                "/bin/firewall-cmd --zone=public --add-port=%(port_num)s/tcp --add-port=%(port_num)s/udp" % {
                    "port_num": kwargs['service_info']['port']
                })

        return self.getPid()

    def stop(self, **kwargs):
        try:
            self.host_platform.execute("/bin/systemctl stop %s.service" % self.service_name)
            if "service_info" in kwargs.keys():
                self.host_platform.execute(
                    "/bin/firewall-cmd --zone=public --remove-port=%(port_num)s/tcp --remove-port=%(port_num)s/udp" % {
                        "port_num": kwargs['service_info']['port']
                    })
        except ShellCommandError as e:
            handled = False
            non_fatal = [
                "service not loaded",
            ]

            for part in non_fatal:
                if part in e.message:
                    handled = True

            if not handled:
                raise

        self.host_platform.execute("/bin/systemctl disable %s.service" % self.service_name)
