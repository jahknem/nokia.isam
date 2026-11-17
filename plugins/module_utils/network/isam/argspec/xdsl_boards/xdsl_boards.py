# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Xdsl_boardsArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_xdsl_boards module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "boards": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "board_id": {"type": "str", "required": True},
                        "admin_state": {"type": "str", "choices": ["up", "down"]},
                        "card_type": {"type": "str"},
                        "dpbo_profile": {"type": "str"},
                        "vce_profile": {"type": "str"},
                        "vplt_autodiscover": {"type": "str"},
                        "vce_capacity_mode": {"type": "str"},
                        "leg_upbo_profile": {"type": "str"},
                        "vect_class": {"type": "str"},
                        "vect_fallback": {
                            "type": "dict",
                            "options": {
                                "fb_vplt_com_fail": {"type": "bool"},
                                "fb_cpe_cap_mism": {"type": "bool"},
                                "fb_conf_not_feas": {"type": "bool"},
                                "spectrum_profile": {"type": "str"},
                                "service_profile": {"type": "str"},
                                "dpbo_profile": {"type": "str"},
                                "rtx_profile": {"type": "str"},
                                "sos_profile": {"type": "str"},
                            },
                        },
                        "auto_port_reset": {
                            "type": "dict",
                            "options": {
                                "max_retry_attempt": {"type": "int"},
                                "reset_interval": {"type": "int"},
                                "reset_threshold": {"type": "int"},
                            },
                        },
                    },
                },
                "vp_boards": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "vp_board_id": {"type": "str", "required": True},
                        "admin_state": {"type": "str", "choices": ["up", "down"]},
                        "vp_links": {
                            "type": "list",
                            "elements": "dict",
                            "options": {
                                "link_id": {"type": "str", "required": True},
                                "lt_expect": {"type": "str"},
                            },
                        },
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
