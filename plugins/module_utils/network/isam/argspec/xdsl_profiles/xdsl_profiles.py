# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


COMMON_PROFILE_OPTIONS = {
    "id": {"type": "int", "required": True},
    "name": {"type": "str"},
    "version": {"type": "int"},
    "active": {"type": "bool"},
    "commands": {"type": "list", "elements": "str"},
}


class Xdsl_profilesArgs(object):
    """The arg spec for the isam_xdsl_profiles module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "service_profiles": {
                    "type": "list",
                    "elements": "dict",
                    "options": dict(COMMON_PROFILE_OPTIONS, **{
                        "max_bitrate_down": {"type": "int"},
                        "max_bitrate_up": {"type": "int"},
                        "max_delay_down": {"type": "int"},
                        "max_delay_up": {"type": "int"},
                    }),
                },
                "spectrum_profiles": {
                    "type": "list",
                    "elements": "dict",
                    "options": dict(COMMON_PROFILE_OPTIONS, **{
                        "dis_ansi_t1413": {"type": "bool"},
                        "dis_etsi_dts": {"type": "bool"},
                        "dis_g992_1_a": {"type": "bool"},
                        "dis_g992_1_b": {"type": "bool"},
                        "dis_g992_2_a": {"type": "bool"},
                        "dis_g992_3_a": {"type": "bool"},
                        "dis_g992_3_b": {"type": "bool"},
                        "g992_5_b": {"type": "bool"},
                        "g992_5_aj": {"type": "bool"},
                        "dis_etsi_ts": {"type": "bool"},
                        "g993_2_17a": {"type": "bool"},
                        "rf_band_list": {"type": "str"},
                    }),
                },
                "dpbo_profiles": {
                    "type": "list",
                    "elements": "dict",
                    "options": dict(COMMON_PROFILE_OPTIONS, **{
                        "es_elect_length": {"type": "int"},
                        "es_cable_model_a": {"type": "int"},
                        "es_cable_model_b": {"type": "int"},
                        "es_cable_model_c": {"type": "int"},
                        "min_usable_signal": {"type": "int"},
                        "min_frequency": {"type": "int"},
                        "max_frequency": {"type": "int"},
                        "rs_elect_length": {"type": "int"},
                    }),
                },
                "vect_profiles": {
                    "type": "list",
                    "elements": "dict",
                    "options": dict(COMMON_PROFILE_OPTIONS, **{
                        "band_control_up": {"type": "str"},
                        "band_control_dn": {"type": "str"},
                    }),
                },
                "vce_profiles": {
                    "type": "list",
                    "elements": "dict",
                    "options": dict(COMMON_PROFILE_OPTIONS, **{
                        "vce_join_timeout": {"type": "str"},
                    }),
                },
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"],
            "default": "merged",
        },
    }
