# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Isam_voice_sipArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_voice_sip module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "registrar": {
                    "type": "dict",
                    "options": {
                        "server": {"type": "str"},
                        "port": {"type": "int"},
                        "realm": {"type": "str"},
                    },
                },
                "proxy": {
                    "type": "dict",
                    "options": {
                        "server": {"type": "str"},
                        "port": {"type": "int"},
                    },
                },
                "codec": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "priority": {"type": "int", "required": True},
                        "type": {"type": "str"},
                    },
                },
                "sip_profile": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "name": {"type": "str", "required": True},
                        "timer_t1": {"type": "int"},
                        "timer_t2": {"type": "int"},
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
