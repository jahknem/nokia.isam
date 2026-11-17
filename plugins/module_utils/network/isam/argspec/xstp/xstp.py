# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class XstpArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_xstp module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "general": {
                    "type": "dict",
                    "options": {
                        "enable_stp": {"type": "bool", "aliases": ["enable-stp"]},
                        "region_name": {"type": "str", "aliases": ["region-name"]},
                        "priority": {"type": "int"},
                        "max_instance_num": {"type": "int"},
                        "max_age": {"type": "int"},
                        "hello_time": {"type": "int"},
                        "forward_delay": {"type": "int"},
                        "version": {"type": "str", "choices": ["stp-compatible", "rstp", "mstp"]},
                        "tx_hold_count": {"type": "int"},
                        "path_cost_type": {"type": "str", "choices": ["16-bit", "32-bit"]},
                        "max_hop_count": {"type": "int"},
                        "region_version": {"type": "int"},
                        "config_id_sel": {"type": "int"},
                    },
                },
                "ports": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "port": {"type": "str", "aliases": ["id", "name"]},
                        "path_cost": {"type": "int", "aliases": ["path-cost"]},
                        "priority": {"type": "int"},
                        "enable_stp": {"type": "bool"},
                        "edge_port": {"type": "bool"},
                        "admin_p2p": {"type": "str", "choices": ["force-true", "force-false", "auto"]},
                        "hello_time": {"type": "int"},
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
