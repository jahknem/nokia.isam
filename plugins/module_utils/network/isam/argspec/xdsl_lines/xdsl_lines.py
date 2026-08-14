# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The arg spec for the isam_xdsl_lines module.
"""


class Xdsl_linesArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_xdsl_lines module."""

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "name": {"type": "str", "required": True, "aliases": ["if_index"]},
                "service_profile": {"type": "str", "aliases": ["service-profile"]},
                "spectrum_profile": {"type": "str", "aliases": ["spectrum-profile"]},
                "dpbo_profile": {"type": "str", "aliases": ["dpbo-profile"]},
                "vect_profile": {"type": "str", "aliases": ["vect-profile"]},
                "rtx_profile": {"type": "str", "aliases": ["rtx-profile"]},
                "sos_profile": {"type": "str", "aliases": ["sos-profile"]},
                "admin_up": {"type": "bool", "aliases": ["admin-up"]},
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


for _field in (
    "ansi_t1413", "etsi_dts", "g992_1_a", "g992_1_b", "g992_2_a", "g992_3_a",
    "g992_3_b", "g992_3_aj", "g992_3_l1", "g992_3_l2", "g992_3_am", "g992_5_a",
    "g992_5_b", "ansi_t1_424", "etsi_ts", "itu_g993_1", "ieee_802_3ah",
    "g992_5_aj", "g992_5_am", "g993_2_8a", "g993_2_8b", "g993_2_8c",
    "g993_2_8d", "g993_2_12a", "g993_2_12b", "g993_2_17a", "g993_2_30a",
    "g993_2_35b", "imp_noise_sensor", "auto_switch",
):
    Xdsl_linesArgs.argument_spec["config"]["options"][_field] = {"type": "bool"}

Xdsl_linesArgs.argument_spec["config"]["options"].update(
    {
        "carrier_data_mode": {"type": "str", "choices": ["off", "on", "on-init"]},
        "transfer_mode": {"type": "str", "choices": ["atm", "ptm", "system-default"]},
        "vect_qln_mode": {"type": "str", "choices": ["without-cancel", "with-cancel"]},
        "vect_fallback": {"type": "str", "choices": ["auto", "forced"]},
    }
)
