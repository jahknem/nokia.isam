from __future__ import absolute_import, division, print_function


class Isam_dhcp_relay_port_statsArgs(object):
    argument_spec = {
        "config": {
            "type": "list",
            "required": True,
            "elements": "dict",
            "options": {
                "port": {"type": "str", "required": True},
                "clear_statistics": {"type": "bool", "default": False},
            },
        },
    }
