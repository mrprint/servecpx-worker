__author__ = 'nolka'

import os


class MinecraftConfig(object):
    def __init__(self, filename):
        self.filename = filename
        self.params = list()

    def open(self):
        if os.path.exists(self.filename):
            with open(self.filename) as f:
                for line in f:
                    self.parse(line.strip())

    def parse(self, line):
        if line.startswith("#"):
            self.params.append(line)
            return
        if "=" in line:
            self.params.append(line.split("=", 1))

    def search(self, name):
        for _id, item in enumerate(self.params):
            if isinstance(item, list):
                if item[0] == name:
                    return _id
        raise ValueError("Parameter not found")

    def get(self, name, cast_to=str):
        try:
            pos = self.search(name)
            return cast_to(self.params[pos][1])
        except:
            return None

    def set(self, name, value):
        try:
            _id = self.search(name)
            self.params[_id][1] = str(value)
        except:
            self.params.append([name, str(value)])

    def save(self):
        with open(self.filename, "w") as f:
            for rec in self.params:
                if isinstance(rec, list):
                    rec = "=".join(rec)
                f.write("%s\n" % rec)