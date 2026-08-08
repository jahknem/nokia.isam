# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Generic_ponArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_generic_pon module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "dpinteg_threshold": {"type": "int"},
                "utilization": {
                    "type": "dict",
                    "options": {
                        "pon_pmcollect": {"type": "bool"},
                        "ont_pmcollect": {"type": "bool"},
                    },
                },
                "ont": {
                    "type": "dict",
                    "options": {
                        "slid_mode": {"type": "bool"},
                        "sn_bundle_timer": {"type": "bool"},
                        "sw_ver_mis_block": {"type": "bool"},
                        "sn_autounlock": {"type": "bool"},
                    },
                },
                "alarmflag": {
                    "type": "dict",
                    "options": {
                        "ponlos_alarm_ctrl": {"type": "bool"},
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
