# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function


class Isam_ipv6_antispoofing_slotArgs(object):
    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "name": {"type": "str", "required": True},
                # Range 64..128 (device type ipv6::bitLength) is enforced by the config class.
                "bit_len": {"type": "int"},
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"],
            "default": "merged",
        },
    }
