# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Isam_voice_sipArgs(object):
    """The arg spec for the isam_voice_sip module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "lineid_syn_prof": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "name": {"type": "str", "required": True},
                        "syntax_pattern": {"type": "bool"},
                        "pots_syntax": {"type": "bool"},
                        "isdn_syntax": {"type": "str"},
                        "cas_r2_syntax": {"type": "bool"},
                        "cas_r1_syntax": {"type": "bool"},
                    },
                },
                "vsp": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "name": {"type": "str", "required": True},
                        "domain_name": {"type": "str"},
                        "admin_status": {"type": "bool"},
                        "tinfo": {"type": "bool"},
                        "ta4": {"type": "bool"},
                        "ttir1": {"type": "bool"},
                        "t_acm_delta": {"type": "bool"},
                        "access_held_time": {"type": "bool"},
                        "awaiting_time": {"type": "bool"},
                        "digit_send_mode": {"type": "bool"},
                        "overlap_484_act": {"type": "bool"},
                        "dmpm_intdg": {"type": "bool"},
                        "timer_b": {"type": "int"},
                        "timer_f": {"type": "int"},
                        "timer_t1": {"type": "int"},
                        "timer_t2": {"type": "int"},
                    },
                },
                "register": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "name": {"type": "str", "required": True},
                        "register_uri": {"type": "bool"},
                        "register_intv": {"type": "bool"},
                        "reg_retry_intv": {"type": "bool"},
                        "reg_prev_ava_intv": {"type": "bool"},
                        "reg_head_start": {"type": "bool"},
                        "reg_start_min": {"type": "bool"},
                        "init_reg_delay": {"type": "bool"},
                    },
                },
                "redundancy": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "name": {"type": "str", "required": True},
                        "support_redun": {"type": "bool"},
                        "dns_purge_timer": {"type": "bool"},
                        "dns_ini_retr_int": {"type": "bool"},
                        "dns_max_retr_nbr": {"type": "bool"},
                        "fg_monitor_method": {"type": "bool"},
                        "fg_monitor_int": {"type": "bool"},
                        "bg_monitor_method": {"type": "bool"},
                        "bg_monitor_int": {"type": "bool"},
                        "stable_obs_period": {"type": "bool"},
                        "fo_hystersis": {"type": "bool"},
                        "del_upd_threshold": {"type": "bool"},
                    },
                },
                "system": {
                    "type": "dict",
                    "options": {
                        "session_timer": {"type": "bool"},
                        "status": {"type": "bool"},
                        "min_se_time": {"type": "bool"},
                        "se_time": {"type": "bool"},
                        "admin_status": {"type": "bool"},
                    },
                },
                "redundancy_cmd": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "name": {"type": "str", "required": True},
                        "start_time": {"type": "bool"},
                        "end_time": {"type": "bool"},
                        "fail_x_type": {"type": "str"},
                        "geo_fail_over": {"type": "str"},
                    },
                },
                "statistics": {
                    "type": "dict",
                    "options": {
                        "stats_5min_config": {"type": "bool"},
                        "cdr_config": {"type": "bool"},
                        "per_line": {"type": "bool"},
                        "per_board": {"type": "bool"},
                        "per_system": {"type": "bool"},
                        "per_call": {"type": "bool"},
                        "out_any_rsp": {"type": "bool"},
                        "out_180_rsp": {"type": "bool"},
                        "out_200_rsp": {"type": "bool"},
                        "in_any_rsp": {"type": "bool"},
                        "in_180_rsp": {"type": "bool"},
                        "in_200_rsp": {"type": "bool"},
                    },
                },
                "cas_nsm_prof": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "name": {"type": "str", "required": True},
                        "international_prefix": {"type": "str"},
                        "country_code": {"type": "str"},
                        "outg_cpn_length": {"type": "int"},
                        "version_nbr": {"type": "bool"},
                        "outg_from_no_cgpn": {"type": "bool"},
                        "national_prefix": {"type": "bool"},
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
