# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Isam_dhcp_serverArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_dhcp_server module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "start_addr": {"type": "str"},
                "end_addr": {"type": "str"},
                "subnet_mask": {"type": "str"},
                "lease_time": {"type": "int"},
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
