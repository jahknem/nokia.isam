# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Pon_interfacesArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_pon_interfaces module."""

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "name": {"type": "str", "required": True},
                "label": {"type": "str"},
                "fec_dn": {"type": "str", "choices": ["enable", "disable"]},
                "ponid_interval": {"type": "int"},
                "ponid_identifier": {"type": "str"},
                "tconts_per_frame": {"type": "int"},
                "admin_state": {"type": "str", "choices": ["up", "down"]},
                "tc_layer": {
                    "type": "dict",
                    "options": {
                        "pm_collect": {
                            "type": "str",
                            "choices": ["none", "pm-enable", "tca-enable"],
                        },
                        "tca_enable": {"type": "bool"},
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
