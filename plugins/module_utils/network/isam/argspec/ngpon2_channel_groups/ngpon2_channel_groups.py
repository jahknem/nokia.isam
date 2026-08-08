# -*- coding: utf-8 -*-

class Ngpon2_channel_groupsArgs(object):
    argument_spec = {
        "config": {"type": "list", "elements": "dict", "options": {
            "id": {"type": "int", "required": True},
            "name": {"type": "str"}, "polling_period": {"type": "int"},
            "raman_reduct": {"type": "str"}, "ng2sys_id": {"type": "str"},
            "admin_state": {"type": "str", "choices": ["up", "down"]},
            "channel_pairs": {"type": "list", "elements": "str"},
            "subchannel_groups": {"type": "list", "elements": "dict", "options": {
                "id": {"type": "int", "required": True}, "name": {"type": "str"},
                "auth_method": {"type": "str"}, "mcast_encrypt": {"type": "str"},
                "fec_dn": {"type": "str"}, "closest_ont": {"type": "int"},
                "diff_reach": {"type": "int"}, "admin_state": {"type": "str", "choices": ["up", "down"]},
                "cpi": {"type": "str"}, "channel_pairs": {"type": "list", "elements": "str"},
            }},
        }},
        "running_config": {"type": "str"},
        "state": {"type": "str", "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"], "default": "merged"},
    }
