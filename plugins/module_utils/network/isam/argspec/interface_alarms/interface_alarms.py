# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Interface_alarmsArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_interface_alarms module."""

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "name": {"type": "str", "required": True},
                "default_severity": {
                    "type": "str",
                    "choices": [
                        "indeterminate",
                        "warning",
                        "minor",
                        "major",
                        "critical",
                    ],
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
