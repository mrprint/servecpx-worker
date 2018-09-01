# -*- coding: utf8
__author__ = 'nolka'

import json
from system.lib import VarExpander

json_str = """
{
    "service": {
        "id": 15,
        "host_server_id": 1,
        "platform_id": 1,
        "account_id": 177,
        "guid": "ff3f16b8-a0ab-495a-a1fb-7e62c15295bf",
        "address": "192.168.1.116",
        "port": 7856,
        "login": null,
        "password": null,
        "keyfile": null,
        "rcon": "J59JV1FSMN",
        "cost": "199.50",
        "date_created": "2014-08-04 16:00:17.090176",
        "is_online": false,
        "is_freeze": false,
        "is_blocked": false,
        "is_installed": true,
        "is_reserved": false,
        "pid": -1,
        "name": "<Unnamed>",
        "state": null
    },
    "service_config": {
        "maxplayers": "50"
    },
    "account": {
        "id": 177,
        "guid": "93d26c63-7ef3-4e01-a9e4-ca3d25661fcd",
        "nick_name": "nolka",
        "email": "email@email.com",
        "first_name": "Тоха",
        "last_name": "Сахаров",
        "password": "G7h/SEeSFqrDjCrZbajT7mTJJwlVU4tLWyrlaFLgX2E=",
        "balance": "406.58",
        "secret": "a59b1fb9-501a-404c-aba1-1224fc1a46c7",
        "date_registered": "2014-07-02 01:07:03+08",
        "date_last_login": "2014-08-04 15:46:12+08",
        "is_blocked": 0,
        "is_confirmed": 0,
        "role": null,
        "invited_by": null,
        "invite_bonus": 15,
        "is_deleted": false,
        "comment": null
    },
    "platform": {
        "id": 1,
        "guid": "3dc1dee2-720c-11e2-85bb-f46d0439aefd",
        "name": "San Andreas Multiplayer",
        "description": "San andreas multiplayer",
        "install_file": "/opt/samp03xsvr_R1-2.tar.gz",
        "install_path": "~/",
        "is_compressed": 1,
        "is_enabled": 1,
        "version": "0.3x",
        "executable_hash": "1dca83340dfeb7f18674dccebe6064e638749a96",
        "executable_name": "samp03svr",
        "launcher_hash": "",
        "launcher_name": "",
        "class": "SampHelper",
        "date_created": "2013-02-08 16:35:40",
        "alias": "samp"
    },
    "local_user_name": "no_user_name"
}
"""
obj = json.loads(json_str)
#print obj

s = VarExpander()
s.add_vars(obj)
print(s.expand("""
# rc - System V runlevel compatibility
#
# This task runs the old System V-style rc script when changing between
# runlevels.

description     "GameCP service instance for user {account.nick_name}({account.email})"
author          "xternalx aka nolka <xternalx@gmail.com>"

start on runlevel [2345]
stop on runlevel [016]

setuid {account.nick_name}
setguid {account.nick_name}

respawn
script
    cd ~/{platform.alias}_{service.id} {azazaza}
    ./{platform.executable_name} -f server.cfg {service.lol}
end script

{local_user_name}

"""))