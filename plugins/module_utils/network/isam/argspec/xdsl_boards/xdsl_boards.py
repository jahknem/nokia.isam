# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Xdsl_boardsArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_xdsl_boards module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "boards": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "board_id": {"type": "str", "required": True},
                        "admin_state": {"type": "str", "choices": ["up", "down"]},
                        "card_type": {"type": "str"},
                        "dpbo_profile": {"type": "str"},
                        "vce_profile": {"type": "str"},
                    },
                },
                "vp_boards": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "vp_board_id": {"type": "str", "required": True},
                        "admin_state": {"type": "str", "choices": ["up", "down"]},
                        "lt_expect": {"type": "str"},
                        "vp_link": {"type": "str"},
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
