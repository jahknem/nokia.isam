# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The arg spec for the isam_ethernet_onts module
"""


class Ethernet_ontsArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_ethernet_onts module
    """

    auto_detect_choices = [
        "10_100baset-auto",
        "10baset-fd",
        "100baset-fd",
        "1000baset-fd",
        "auto-basetfd",
        "10gig-fd",
        "2.5gig-fd",
        "5gig-fd",
        "10baset-auto",
        "10baset-hd",
        "100baset-hd",
        "1000baset-hd",
        "autobaset-hd",
        "10_100_1000baset-auto",
        "100baset-auto",
        "auto",
        "1000baset-auto",
    ]

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "uni_idx": {"type": "str", "required": True, "aliases": ["name"]},
                "cust_info": {"type": "str"},
                "auto_detect": {"type": "str", "choices": auto_detect_choices},
                "power_control": {"type": "str", "choices": ["enable", "disable"]},
                "pse_class": {"type": "str", "choices": ["0", "1", "2", "3", "4", "5"]},
                "pse_pw_priority": {"type": "str", "choices": ["critical", "high", "low"]},
                "pwr_override": {"type": "str", "choices": ["enable", "disable"]},
                "lpt_mode": {"type": "str", "choices": ["not-supported", "enabled", "disabled"]},
                "admin_state": {"type": "str", "choices": ["up", "down"]},
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
