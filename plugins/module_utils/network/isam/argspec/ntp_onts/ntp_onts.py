# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The arg spec for the isam_ntp_onts module
"""


class Ntp_ontsArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_ntp_onts module"""

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "ont_id": {"type": "str", "required": True},
                "server": {"type": "str"},
                "port": {"type": "int"},
                "poll_interval": {"type": "int"},
                "enable": {"type": "bool"},
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
