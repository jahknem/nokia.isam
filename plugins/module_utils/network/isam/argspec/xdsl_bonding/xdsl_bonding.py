# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Xdsl_bondingArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_xdsl_bonding module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "group_assembly_time": {"type": "int"},
                "ptm_init_mode": {"type": "str", "choices": ["mode1", "mode2"]},
                "groups": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "group_id": {"type": "str", "required": True},
                        "group_profile": {"type": "str"},
                        "group_rtx_profile": {"type": "str"},
                        "up": {"type": "bool"},
                    },
                },
                "boards": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "board_id": {"type": "str", "required": True},
                        "vect_fallback": {
                            "type": "dict",
                            "options": {
                                "group_profile": {"type": "str"},
                                "group_rtx_profile": {"type": "str"},
                            },
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
