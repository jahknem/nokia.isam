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
                "client_state": {"type": "str", "choices": ["on", "off"]},
                "config_mode": {"type": "str", "choices": ["dhcp", "manual"]},
                "server1_ip_addr": {"type": "str"},
                "server2_ip_addr": {"type": "str"},
                "server3_ip_addr": {"type": "str"},
                "oper_mode": {"type": "str", "choices": ["unicast", "multicast", "broadcast"]},
                "key_identifier": {"type": "int"},
                "key": {"type": "str", "no_log": True},
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
