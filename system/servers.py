# -*- coding: utf8

__author__ = 'nolka'

import pwd
import os
import crypt
import subprocess

from system.lib.tools import getLogger
from system.lib import VarExpander
from system.exceptions import ShellCommandError
import options


class ExecResult(object):
    def __init__(self, status_code, stdout, stderr):
        self.code = status_code
        if status_code == 0:
            self.success = True
        else:
            self.success = False

        self.stdout = stdout
        self.stderr = stderr


class HostServer(object):
    def __init__(self):
        self.logger = getLogger(type(self).__name__)

    def get_user_info(self, name):
        try:
            return pwd.getpwnam(name)
        except KeyError:
            return None

    def create_user(self, name, password):
        hash = crypt.crypt(password, "1ayC9esdtw23I")
        return self.execute(options.cmd_create_user % {
            "password": hash,
            "login": name,
        })

    def execute(self, command, attributes=None):
        # Если нам передали дополнительные атрибуты, значит команда является шаблоном, и его нужно
        #   сначала скомпилить
        if isinstance(attributes, dict):
            ve = VarExpander(attributes)
            command = ve.expand(command)

        self.logger.debug("Execing command %s" % command)
        proc = subprocess.Popen(command, shell=True, executable="/bin/bash", stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        buffers = proc.communicate()

        self.exec_result = ExecResult(proc.returncode, *buffers)

        self.logger.debug("Command [%s] has been ended with code %d\nstdout: %s\nstderr: %s" % (
            command, self.exec_result.code, self.exec_result.stdout, self.exec_result.stderr))

        if self.exec_result.code == 0:
            return True, self.exec_result.stdout, self.exec_result.stderr
        else:
            raise ShellCommandError("Shell error", self.exec_result.code, self.exec_result.stdout, self.exec_result.stderr)

    def cp(self, src, dest, username, overwrite=True):
        return self.execute(options.cmd_copy_file % {
            "user": username,
            "from": src,
            "to": dest
        })

    def rm(self, target):
        return self.execute("%s -fr" % target)

    def cd(self, dir):
        self.last_wd = os.getcwd()
        self.logger.debug("Chdir to %s" % dir)
        os.chdir(dir)
        return self.last_wd
