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
                    },
                },
                "ports": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "port": {"type": "str", "aliases": ["id", "name"]},
                        "path_cost": {"type": "int", "aliases": ["path-cost"]},
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
