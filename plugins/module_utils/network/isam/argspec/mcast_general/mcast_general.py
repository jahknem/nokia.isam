# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Mcast_generalArgs(object):
    """The arg spec for the isam_mcast_general module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "admin_state": {"type": "bool"},
                "forward_method": {"type": "str"},
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
