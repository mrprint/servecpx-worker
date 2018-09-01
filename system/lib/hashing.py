# -*- coding: utf8 -*-
__author__ = 'nolka'

import hashlib

def file_get_sha1(filename):
    BLOCKSIZE = 4096
    hasher = hashlib.sha1()
    with open(filename, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()