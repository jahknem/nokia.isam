# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Isam_vlan_globalArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_vlan_global module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "broadcast_frames": {
                    "type": "dict",
                    "options": {
                        "drop_unknown_multicast": {"type": "bool"},
                    },
                },
                "priority_regen": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "dot1p": {"type": "int", "required": True},
                        "regen_dot1p": {"type": "int"},
                    },
                },
                "tpid": {
                    "type": "dict",
                    "options": {
                        "value": {
                            "type": "str",
                            "choices": ["8100", "9100", "88a8", "9200"],
                        },
                    },
                },
                "vmac_address_format": {
                    "type": "dict",
                    "options": {
                        "format": {
                            "type": "str",
                            "choices": ["canonical", "non-canonical"],
                        },
                    },
                },
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": [
                "merged",
                "replaced",
                "overridden",
                "deleted",
                "gathered",
                "rendered",
                "parsed",
            ],
            "default": "merged",
        },
    }
