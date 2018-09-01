# -*- coding: utf8 -*-
__author__ = 'nolka'

import re


def utfize(text):
    return unicode(text, 'utf8', 'replace') if type(text).__name__ != "unicode" else text


class VarExpander(object):
    """ Класс для разворачивания шаблонов чего-либо в форму, пригодную к применению """

    def __init__(self, initial_data=None):
        self.variables = dict()
        if initial_data:
            self.add_vars(initial_data)

    def add_vars(self, variables):
        if isinstance(variables, dict):
            for obj, values in variables.iteritems():
                self.variables[obj] = values
        else:
            raise Exception("Unknown variable type specified!")
        return self

    def expand(self, script, clear_unknown=True):
        r = re.compile("\{([^\s\}]+)\}")
        matches = r.findall(script)
        for match in matches:
            if "." not in match:
                if match in self.variables.keys():
                    replace_with = self.variables.get(match)
                    script = script.replace("{%s}" % match, replace_with)
                else:
                    if clear_unknown:
                        replace_with = ""
                        script = script.replace("{%s}" % match, replace_with)

                continue

            obj, path_parts = match.split(".", 1)
            if obj not in self.variables.keys():
                if clear_unknown:
                    script = script.replace("{%s}" % match, "")
                continue

            sub = self.variables[obj]
            for attr in path_parts.split("."):
                if attr in sub.keys():
                    sub = sub.get(attr)
                else:
                    sub = ""
            script = script.replace("{%s}" % match, str(sub))
        return script

