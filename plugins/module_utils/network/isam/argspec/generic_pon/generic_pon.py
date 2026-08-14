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
                        "threshold": {
                            "type": "dict",
                            "options": {
                                field: {"type": "str"}
                                for field in (
                                    "txmcutilhi", "txmcutilmd", "txmcutillo",
                                    "txtotutilhi", "txtotutilmd", "txtotutillo",
                                    "rxtotutilhi", "rxtotutilmd", "rxtotutillo",
                                    "dbacongperiodhi", "dbacongperiodmd", "dbacongperiodlo",
                                    "txucdropfrmhi", "txucdropfrmmd", "txucdropfrmlo",
                                    "txmcdropfrmhi", "txmcdropfrmmd", "txmcdropfrmlo",
                                    "txbcdropfrmhi", "txbcdropfrmmd", "txbcdropfrmlo",
                                    "rxtotdropfrmhi", "rxtotdropfrmmd", "rxtotdropfrmlo",
                                    "numtcint", "numtcintdba", "dbacongthresh",
                                )
                            },
                        },
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
