# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

#############################################
#                WARNING                    #
#############################################
#
# This file is auto generated by the
# cli_rm_builder.
#
# Manually editing this file is not advised.
#
# To update the argspec make the desired changes
# in the module docstring and re-run
# cli_rm_builder.
#
#############################################

"""
The arg spec for the isam_ont_interfaces module
"""


class Ont_interfacesArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_ont_interfaces module
    """

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "ont_idx": {"type": "int"},
                "battery_bkup": {"type": "bool"},
                "berint": {"type": "int"},
                "desc1": {"type": "str"},
                "desc2": {"type": "str"},
                "provversion": {"type": "str"},
                "sernum": {"type": "str"},
                "subslocid": {"type": "str"},
                "sw_ver_pland": {"required": True},
                "fec_up": {"type": "bool"},
                "bridge_map_mode": {
                    "type": "str",
                    "choices": [
                        "1-mp-bridge-map-filter",
                        "n-p-bridge-map-filter",
                        "n-mp-bridge-map-filter",
                    ],
                },
                "pwr_shed_prof_id": {"type": "int"},
                "ont_enable": {"type": "bool"},
                "p2p_enable": {"type": "bool"},
                "optics_hist": {"type": "bool"},
                "sw_dnload_version": {"type": "str"},
                "plnd_var": {"type": "str"},
                "rf_filter": {
                    "type": "str",
                    "choices": [
                        "pass-low-high",
                        "pass-low-middle",
                        "pass-low",
                        "pass-none",
                    ],
                },
                "us_police_mode": {
                    "type": "str",
                    "choices": ["local", "remote", "network"],
                },
                "enable_aes": {"type": "bool"},
                "voip_allowed": {
                    "type": "str",
                    "choices": ["enable", "disable", "iphost", "veip"],
                },
                "iphc_allowed": {"type": "bool"},
                "slid_visibility": {
                    "type": "str",
                    "choices": ["disabled", "enabled-slid-on", "enabled-all"],
                },
                "log_auth_id": {"type": "int"},
                "log-auth-pwd": {"type": "str"},
                "cvlantrans_mode": {"type": "str", "choices": ["remote", "local"]},
                "sn_bundle_ctrl": {
                    "type": "str",
                    "choices": ["unbundle", "bundle", "auto"],
                },
                "pland_cfgfile1": {"type": "str"},
                "pland_cfgfile2": {"type": "str"},
                "dnload_fgfile1": {"type": "str"},
                "dnload_cfgfile2": {"type": "str"},
                "us_tcpolice_mode": {
                    "type": "str",
                    "choices": ["local", "remote"],
                },
                "planned_us_rate": {
                    "choices": ["nominal-line-rate", "2.5G", "10G"]
                },
                "admin-state": {"type": "str", "choices": ["up", "down"]},
                "oltdscppbitalign": {"type": "bool"},
                "pref_channel_pair": {"type": "str"},
                "prot-channel-pair": {"type": "str"},
                "alt_pref_ch_pair": {"type": "str"},
                "ratelimit_us_dhcp": {"type": "int"},
                "ratelimit-us-arp": {"type": "int"},
                "flush-mac": {"type": "bool"},
            },
        },
        "state": {
            "type": "str",
            "choices": ["gathered", "merged", "replaced", "overridden", "deleted"],
            "default": "merged",
        },
    }  # pylint: disable=C0301
