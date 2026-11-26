from __future__ import absolute_import, division, print_function


class Isam_ethernet_statisticsArgs(object):
    argument_spec = {
        "config": {
            "type": "list",
            "required": True,
            "elements": "dict",
            "options": {
                "port": {"type": "str", "required": True},
                "clear_stats": {"type": "bool", "default": False},
            },
        },
    }
