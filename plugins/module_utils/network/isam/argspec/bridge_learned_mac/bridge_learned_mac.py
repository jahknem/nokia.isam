from __future__ import absolute_import, division, print_function


class Isam_bridge_learned_macArgs(object):
    argument_spec = {
        "config": {
            "type": "list",
            "required": True,
            "elements": "dict",
            "options": {
                "vlan_port": {"type": "str", "required": True},
                "mac_address": {"type": "str", "required": True},
                "delete": {"type": "bool", "default": False},
            },
        },
    }
