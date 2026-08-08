# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function


class Isam_ipv6_antispoofing_slotArgs(object):
    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "name": {"type": "str", "required": True},
                "bit_len": {"type": "int", "min": 64, "max": 128, "default": 64},
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"],
            "default": "merged",
        },
    }
