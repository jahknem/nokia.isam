# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Ani_ontsArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_ani_onts module."""

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "ont_idx": {"type": "str", "required": True},
                "tca_profile": {"type": "str"},
                "admin_state": {"type": "str", "choices": ["up", "down"]},
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
