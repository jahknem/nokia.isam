# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Equipment_ontsArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_equipment_onts module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "interfaces": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "ont_idx": {"type": "str", "required": True},
                        "sw_ver_pland": {"type": "str"},
                        "sernum": {"type": "str"},
                        "subslocid": {"type": "str"},
                        "fec_up": {"type": "str"},
                        "sw_dnload_version": {"type": "str"},
                        "plnd_var": {"type": "str"},
                        "enable_aes": {"type": "str"},
                        "log_auth_pwd": {"type": "str", "no_log": True},
                        "cvlantrans_mode": {"type": "str"},
                        "planned_us_rate": {"type": "str"},
                        "admin_state": {"type": "str", "choices": ["up", "down"]},
                    },
                },
                "slots": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "ont_slot_idx": {"type": "str", "required": True},
                        "planned_card_type": {"type": "str"},
                        "plndnumdataports": {"type": "int"},
                        "plndnumvoiceports": {"type": "int"},
                        "port_type": {"type": "str"},
                        "transp_mode_rem": {"type": "str"},
                        "no_mcast_control": {"type": "str"},
                        "admin_state": {"type": "str", "choices": ["up", "down"]},
                    },
                },
                "sw_ctrls": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "sw_ctrl_id": {"type": "int", "required": True},
                        "hw_version": {"type": "str"},
                        "ont_variant": {"type": "str"},
                        "plnd_sw_version": {"type": "str"},
                        "plnd_sw_ver_conf": {"type": "str"},
                        "sw_dwload_ver": {"type": "str"},
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
