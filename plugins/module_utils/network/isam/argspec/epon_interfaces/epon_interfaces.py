# -*- coding: utf-8 -*-

class Epon_interfacesArgs(object):
    argument_spec = {
        "config": {"type": "list", "elements": "dict", "options": {
            "name": {"type": "str", "required": True}, "polling_period": {"type": "int"},
            "dba_polling0": {"type": "int"}, "dba_polling1": {"type": "int"},
            "dba_polling2": {"type": "int"}, "dba_polling3": {"type": "int"},
            "dba_polling4": {"type": "int"}, "admin_state": {"type": "str", "choices": ["up", "down"]},
        }},
        "running_config": {"type": "str"},
        "state": {"type": "str", "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"], "default": "merged"},
    }
