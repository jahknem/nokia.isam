# -*- coding: utf-8 -*-
class Pppoel2Args(object):
    argument_spec = {
        "config": {"type": "list", "elements": "dict", "options": {
            "name": {"type": "str", "required": True}, "enabled": {"type": "bool", "default": True},
        }},
        "running_config": {"type": "str"},
        "state": {"type": "str", "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"], "default": "merged"},
    }
