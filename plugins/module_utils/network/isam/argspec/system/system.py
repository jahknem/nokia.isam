# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Isam_systemArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_system module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "id": {
                    "type": "dict",
                    "options": {
                        "name": {"type": "str"},
                        "location": {"type": "str"},
                        "contact": {"type": "str"},
                        "node_id": {"type": "str"},
                        "nt_intercon_vlan": {"type": "int"},
                        "internal_nw_vlan": {"type": "int"},
                        "system_mac": {"type": "str"},
                        "access_oper_id": {"type": "str"},
                        "system_40gkr4": {"type": "str", "choices": ["disable", "enable"]},
                        "en_snmp_auth_trap": {"type": "bool"},
                        "periph_mgnt_vlan": {"type": "int"},
                        "periph_mgnt_ctrl": {"type": "str", "choices": ["enable", "disable"]},
                        "port_num_in_proto": {"type": "str"},
                        "ont_trc_dbg_vlan": {"type": "int"},
                        "ntr_ssmout_vlan": {"type": "int"},
                        "ntr_ptp_vlan": {"type": "int"},
                        "customer_id": {"type": "str"},
                        "voiceoswp": {"type": "str"},
                        "scalingmode": {"type": "str"},
                        "arp_polling_inter": {"type": "int"},
                        "bsnap_state": {"type": "str"},
                        "bsnap_server_ip": {"type": "str"},
                        "bsnap_server_port": {"type": "int"},
                        "arp_tca_threshold": {"type": "int"},
                    },
                },
                "security": {
                    "type": "dict",
                    "options": {
                        "ssh": {"type": "bool"},
                        "telnet": {"type": "bool"},
                        "snmp": {"type": "bool"},
                        "welcome_banner": {"type": "str"},
                    },
                },
                "sntp": {
                    "type": "dict",
                    "options": {
                        "server": {"type": "str"},
                        "server_ip_addr": {"type": "str"},
                        "port": {"type": "int"},
                        "server_port": {"type": "int"},
                        "poll_interval": {"type": "int"},
                        "polling_rate": {"type": "int"},
                        "enabled": {"type": "bool"},
                        "timezone_offset": {"type": "int"},
                        "servers": {
                            "type": "list",
                            "elements": "dict",
                            "options": {
                                "ip_address": {"type": "str", "required": True},
                                "priority": {"type": "int"},
                            },
                        },
                    },
                },
                "syslog": {
                    "type": "dict",
                    "options": {
                        "server": {"type": "str"},
                        "facility": {"type": "str"},
                        "severity": {"type": "str"},
                        "version": {"type": "str"},
                        "time_format": {"type": "str"},
                        "destinations": {
                            "type": "list",
                            "elements": "dict",
                            "options": {
                                "name": {"type": "str", "required": True},
                                "type": {"type": "str"},
                                "disable": {"type": "bool"},
                                "upload_rotate": {"type": "bool"},
                                "persist_enable": {"type": "bool"},
                                "persist_timer": {"type": "int"},
                            },
                        },
                        "routes": {
                            "type": "list",
                            "elements": "dict",
                            "options": {
                                "destination": {"type": "str", "required": True},
                                "msg_type": {"type": "str"},
                                "facility": {"type": "str"},
                                "severities": {"type": "list", "elements": "str"},
                                "syslog_vlan": {"type": "int"},
                            },
                        },
                    },
                },
                "sync_if_timing": {
                    "type": "dict",
                    "options": {
                        "mode": {"type": "str"},
                        "source": {"type": "str"},
                        "revert": {"type": "bool"},
                        "wait_time": {"type": "int"},
                        "output_ql_thresh": {"type": "str"},
                        "ssmout_en_bits": {"type": "bool"},
                        "ssmout_ceiling": {"type": "str"},
                        "ais_sensitivity": {"type": "str", "choices": ["enable", "disable"]},
                        "bits": {"type": "str"},
                        "bits_bind": {
                            "type": "dict",
                            "options": {
                                "bits_a_bind": {"type": "str"},
                                "bits_b_bind": {"type": "str"},
                            },
                        },
                        "force_reference": {"type": "str"},
                        "ref_order": {
                            "type": "dict",
                            "options": {
                                "prio1": {"type": "str"},
                                "prio2": {"type": "str"},
                            },
                        },
                        "ssm": {
                            "type": "list",
                            "elements": "dict",
                            "options": {
                                "reference": {"type": "str", "required": True},
                                "ssmenable": {"type": "bool"},
                                "default_ql": {"type": "str"},
                                "target_ql": {"type": "str"},
                            },
                        },
                        "synce": {
                            "type": "list",
                            "elements": "dict",
                            "options": {
                                "reference": {"type": "str", "required": True},
                                "port": {"type": "str"},
                            },
                        },
                        "ssmout_synce": {
                            "type": "list",
                            "elements": "dict",
                            "options": {
                                "port": {"type": "str", "required": True},
                                "ssmout_enable": {"type": "bool"},
                            },
                        },
                    },
                },
                "loop_id_syntax": {
                    "type": "dict",
                    "options": {
                        "atm_based_dsl": {"type": "str"},
                        "efm_based_dsl": {"type": "str"},
                        "efm_based_pon": {"type": "str"},
                        "efm_based_epon": {"type": "str"},
                        "efm_based_ngpon2": {"type": "str"},
                    },
                },
                "relay_id_syntax": {
                    "type": "dict",
                    "options": {
                        "atm_based_dsl": {"type": "str"},
                        "efm_based_dsl": {"type": "str"},
                    },
                },
                "transaction": {
                    "type": "dict",
                    "options": {
                        "timeout": {"type": "int"},
                        "time_out_value": {"type": "int"},
                        "log_full_action": {"type": "str"},
                    },
                },
                "max_lt_link_speed": {"type": "str"},
                "external_leds": {
                    "type": "dict",
                    "options": {"status": {"type": "str", "choices": ["disable", "enable"]}},
                },
                "auto_laser_shutdown": {
                    "type": "dict",
                    "options": {"action": {"type": "str"}},
                },
                "auto_switch": {
                    "type": "dict",
                    "options": {
                        "xdsl_atm_ptm": {"type": "bool"},
                        "xdsl_stepup_delay": {"type": "int"},
                    },
                },
                "zero_touch_provision": {
                    "type": "dict",
                    "options": {"action": {"type": "str"}},
                },
                "pon_ont": {
                    "type": "dict",
                    "options": {
                        "slid_mode": {"type": "str"},
                        "pwrbrst_mode": {"type": "str"},
                        "sn_bundle_timer": {"type": "int"},
                        "sw_ver_mis_block": {"type": "str", "choices": ["enable", "disable"]},
                        "sn_autounlock": {"type": "str", "choices": ["disable", "enable"]},
                    },
                },
                "nt_sftp": {
                    "type": "dict",
                    "options": {"write_enable": {"type": "bool"}},
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
