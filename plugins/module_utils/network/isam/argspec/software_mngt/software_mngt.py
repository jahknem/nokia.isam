# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Software_mngtArgs(object):
    """The arg spec for the isam_software_mngt module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "database": {
                    "type": "dict",
                    "options": {
                        "version": {"type": "str"},
                        "url": {"type": "str"},
                    },
                },
                "oswp": {
                    "type": "dict",
                    "options": {
                        "admin_state": {"type": "bool"},
                    },
                },
                "sw_replacement_mode": {
                    "type": "dict",
                    "options": {
                        "mode": {"type": "str"},
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
