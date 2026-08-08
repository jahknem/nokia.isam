# -*- coding: utf-8 -*-

class Channel_pair_pmArgs(object):
    argument_spec = {
        "config": {"type": "list", "elements": "dict", "options": {
            "name": {"type": "str", "required": True},
            "fec_tc_layer": {"type": "str", "choices": ["enable", "disable"]},
            "xg_tc_layer": {"type": "str", "choices": ["enable", "disable"]},
        }},
        "running_config": {"type": "str"},
        "state": {"type": "str", "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"], "default": "merged"},
    }
