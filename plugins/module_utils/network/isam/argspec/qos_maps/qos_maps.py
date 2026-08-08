# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Qos_mapsArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_qos_maps module."""

    _tc_map_dot1p_options = {
        "dot1p": {"type": "int", "required": True},
        "tc": {"type": "int"},
        "dpcolor": {"type": "str"},
        "policer_color": {"type": "str"},
    }

    _dscp_map_dot1p_options = {
        "dscp": {"type": "str", "required": True},
        "dot1p": {"type": "int"},
    }

    _up_ctrl_pkt_options = {
        "protocol": {"type": "str", "required": True},
        "queue": {"type": "int"},
        "profile": {"type": "str"},
    }

    _dn_ctrl_pkt_options = {
        "protocol": {"type": "str", "required": True},
        "queue": {"type": "int"},
        "profile": {"type": "str"},
    }

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "tc_map_dot1p": {
                    "type": "list",
                    "elements": "dict",
                    "options": _tc_map_dot1p_options,
                },
                "dscp_map_dot1p": {
                    "type": "list",
                    "elements": "dict",
                    "options": _dscp_map_dot1p_options,
                },
                "up_ctrl_pkt": {
                    "type": "list",
                    "elements": "dict",
                    "options": _up_ctrl_pkt_options,
                },
                "dn_ctrl_pkt": {
                    "type": "list",
                    "elements": "dict",
                    "options": _dn_ctrl_pkt_options,
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
