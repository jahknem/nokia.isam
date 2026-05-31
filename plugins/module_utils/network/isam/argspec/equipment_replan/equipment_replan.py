# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Equipment_replanArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_equipment_replan module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "board_auto_replan": {
                    "type": "str",
                    "choices": ["enable", "disable"],
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
