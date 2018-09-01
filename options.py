# -*- coding: utf8

import os

from system.paramsparser.base import ModuleRunParams

ROOT = ROOT = os.path.realpath(__file__).rsplit(os.sep, 1)[0]

log_dir = "%s/logs" % ROOT

parser = ModuleRunParams()
print("Using config.%s" % parser.mode)
mdl = __import__("config.%s" % parser.mode, globals(), locals())
mdl = getattr(mdl, parser.mode)

globals().update(mdl.__dict__)