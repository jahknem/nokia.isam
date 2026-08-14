# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Pon_interfacesArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_pon_interfaces module."""

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "name": {"type": "str", "required": True},
                "label": {"type": "str"},
                "fec_dn": {"type": "str", "choices": ["enable", "disable"]},
                "ber_calc_period": {"type": "int", "min": 1, "max": 864000},
                "polling_period": {"type": "int", "min": 1, "max": 864000},
                "sig_degrade_th": {"type": "int", "min": 4, "max": 10},
                "sig_fail_th": {"type": "int", "min": 3, "max": 8},
                "raman_reduct": {"type": "str", "choices": ["enable", "disable"]},
                "closest_ont": {"type": "int", "min": 0, "max": 40},
                "diff_reach": {"type": "int", "choices": [20, 34, 40]},
                "pon_tag": {"type": "str"},
                "pon_id": {"type": "str"},
                "mcast_encrypt": {"type": "str", "choices": ["enable", "disable"]},
                "auth_method": {"type": "str", "choices": ["sn-slid", "logical", "loidpre", "logical-std", "loidpre-std", "loid-sn-slid"]},
                "ponid_interval": {"type": "int", "min": 0, "max": 60},
                "ponid_odn": {"type": "str", "choices": ["a", "b", "bplus", "c", "cplus", "auto"]},
                "ponid_identifier": {"type": "str"},
                "max_ranging_onts": {"type": "int", "min": 0, "max": 128},
                "tconts_per_frame": {"type": "int", "min": 0, "max": 64},
                "pon_speed": {"type": "str", "choices": ["nominal", "10g-10g", "10g-2.5g"]},
                "burst_overhead": {"type": "str", "choices": ["robust", "reduced"]},
                "onu_prov_mode": {"type": "str", "choices": ["semi-auto", "auto"]},
                "admin_state": {"type": "str", "choices": ["up", "down"]},
                "tc_layer": {
                    "type": "dict",
                    "options": {
                        "pm_collect": {
                            "type": "str",
                            "choices": ["none", "pm-enable", "tca-enable"],
                        },
                        "tca_enable": {"type": "bool"},
                    },
                },
                "tc_layer_threshold": {
                    "type": "dict",
                    "options": {
                        "error_frags_up": {"type": "str"},
                    },
                },
                "mcast_tc_layer": {
                    "type": "dict",
                    "options": {
                        "pm_collect": {"type": "str", "choices": ["enable", "disable"]},
                    },
                },
                "phy_layer": {
                    "type": "dict",
                    "options": {
                        "pm_collect": {"type": "str", "choices": ["enable", "disable"]},
                    },
                },
                "fec_tc_layer": {
                    "type": "dict",
                    "options": {
                        "pm_collect": {"type": "str", "choices": ["enable", "disable"]},
                    },
                },
                "xg_tc_layer": {
                    "type": "dict",
                    "options": {
                        "pm_collect": {"type": "str", "choices": ["enable", "disable"]},
                    },
                },
                "otdr": {
                    "type": "dict",
                    "options": {
                        "mode": {"type": "str", "choices": ["enable", "disable", "test"]},
                    },
                },
                "utilization": {
                    "type": "dict",
                    "options": {
                        "pon_pmcollect": {"type": "str", "choices": ["none", "pm-enable", "tca-enable", "inherit"]},
                        "ont_pmcollect": {"type": "str", "choices": ["enable", "disable", "inherit"]},
                        "ontbulk_pmcollect": {"type": "str", "choices": ["enable", "disable"]},
                        "threshold": {
                            "type": "dict",
                            "options": {
                                field: {"type": "str"}
                                for field in (
                                    "txmcutilhi", "txmcutilmd", "txmcutillo",
                                    "txtotutilhi", "txtotutilmd", "txtotutillo",
                                    "rxtotutilhi", "rxtotutilmd", "rxtotutillo",
                                    "dbacongperiodhi", "dbacongperiodmd", "dbacongperiodlo",
                                    "txucdropfrmhi", "txucdropfrmmd", "txucdropfrmlo",
                                    "txmcdropfrmhi", "txmcdropfrmmd", "txmcdropfrmlo",
                                    "txbcdropfrmhi", "txbcdropfrmmd", "txbcdropfrmlo",
                                    "rxtotdropfrmhi", "rxtotdropfrmmd", "rxtotdropfrmlo",
                                    "numtcint", "numtcintdba", "dbacongthresh",
                                )
                            },
                        },
                    },
                },
                "deact_ont_tca": {
                    "type": "dict",
                    "options": {
                        "mode": {"type": "str", "choices": ["disable", "percent", "number"]},
                        "monitor_interval": {"type": "int", "min": 5, "max": 300},
                        "threshold_percent": {
                            "type": "dict",
                            "options": {
                                field: {"type": "int", "min": 1, "max": 100}
                                for field in ("high", "high_clr", "low", "low_clr")
                            },
                        },
                        "threshold_number": {
                            "type": "dict",
                            "options": {
                                field: {"type": "int", "min": 1, "max": 128}
                                for field in ("high", "high_clr", "low", "low_clr")
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
