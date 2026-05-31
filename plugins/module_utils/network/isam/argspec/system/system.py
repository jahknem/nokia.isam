# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Isam_systemArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_system module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "id": {
                    "type": "dict",
                    "options": {
                        "name": {"type": "str"},
                        "location": {"type": "str"},
                        "contact": {"type": "str"},
                    },
                },
                "security": {
                    "type": "dict",
                    "options": {
                        "ssh": {"type": "str"},
                        "telnet": {"type": "str"},
                        "snmp": {"type": "str"},
                    },
                },
                "sntp": {
                    "type": "dict",
                    "options": {
                        "server": {"type": "str"},
                        "port": {"type": "int"},
                        "poll_interval": {"type": "int"},
                    },
                },
                "syslog": {
                    "type": "dict",
                    "options": {
                        "server": {"type": "str"},
                        "facility": {"type": "str"},
                        "severity": {"type": "str"},
                    },
                },
                "sync_if_timing": {
                    "type": "dict",
                    "options": {
                        "mode": {"type": "str"},
                        "source": {"type": "str"},
                    },
                },
                "transaction": {
                    "type": "dict",
                    "options": {
                        "timeout": {"type": "int"},
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
