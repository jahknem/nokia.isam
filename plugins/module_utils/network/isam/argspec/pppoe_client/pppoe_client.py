# -*- coding: utf-8 -*-
class PppoeClientArgs(object):
    argument_spec = {
        "config": {"type": "list", "elements": "dict", "options": {
            "name": {"type": "str", "required": True},
            "ipversion": {"type": "str"}, "authproto": {"type": "str"}, "mru": {"type": "int"},
            "client_id": {"type": "int"}, "profile_name": {"type": "str"},
            "username": {"type": "str"}, "password": {"type": "str", "no_log": True},
            "mac": {"type": "str"}, "pbit": {"type": "int"},
        }},
        "running_config": {"type": "str"},
        "state": {"type": "str", "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"], "default": "merged"},
    }
