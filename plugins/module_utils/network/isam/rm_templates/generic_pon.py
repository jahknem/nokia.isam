# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Generic_ponTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Generic_ponTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "dpinteg_threshold",
            "compval": "dpinteg_threshold",
            "getval": re.compile(
                r"^configure\sgeneric-pon\sdpinteg-threshold\s(?P<dpinteg_threshold>\S+)(?:\s+.*)?$"
            ),
            "setval": "configure generic-pon dpinteg-threshold {{ dpinteg_threshold }}",
            "result": {
                "dpinteg_threshold": "{{ dpinteg_threshold }}",
            },
        },
        {
            "name": "utilization.pon_pmcollect",
            "compval": "pon_pmcollect",
            "getval": re.compile(
                r"^configure\sgeneric-pon\sutilization\s(?P<negate>no\s)?(?P<pon_pmcollect>pon-pmcollect)(?:\s+.*)?$"
            ),
            "setval": "configure generic-pon utilization {{ 'no ' if pon_pmcollect == false else '' }}pon-pmcollect",
            "result": {
                "utilization": {
                    "pon_pmcollect": "{{ False if negate else True }}",
                },
            },
        },
        {
            "name": "utilization.ont_pmcollect",
            "compval": "ont_pmcollect",
            "getval": re.compile(
                r"^configure\sgeneric-pon\sutilization\s(?P<negate>no\s)?(?P<ont_pmcollect>ont-pmcollect)(?:\s+.*)?$"
            ),
            "setval": "configure generic-pon utilization {{ 'no ' if ont_pmcollect == false else '' }}ont-pmcollect",
            "result": {
                "utilization": {
                    "ont_pmcollect": "{{ False if negate else True }}",
                },
            },
        },
        {
            "name": "ont.slid_mode",
            "compval": "slid_mode",
            "getval": re.compile(
                r"^configure\sgeneric-pon\sont\s(?P<negate>no\s)?(?P<slid_mode>slid-mode)(?:\s+.*)?$"
            ),
            "setval": "configure generic-pon ont {{ 'no ' if slid_mode == false else '' }}slid-mode",
            "result": {
                "ont": {
                    "slid_mode": "{{ False if negate else True }}",
                },
            },
        },
        {
            "name": "ont.sn_bundle_timer",
            "compval": "sn_bundle_timer",
            "getval": re.compile(
                r"^configure\sgeneric-pon\sont\s(?P<negate>no\s)?(?P<sn_bundle_timer>sn-bundle-timer)(?:\s+.*)?$"
            ),
            "setval": "configure generic-pon ont {{ 'no ' if sn_bundle_timer == false else '' }}sn-bundle-timer",
            "result": {
                "ont": {
                    "sn_bundle_timer": "{{ False if negate else True }}",
                },
            },
        },
        {
            "name": "ont.sw_ver_mis_block",
            "compval": "sw_ver_mis_block",
            "getval": re.compile(
                r"^configure\sgeneric-pon\sont\s(?P<negate>no\s)?(?P<sw_ver_mis_block>sw-ver-mis-block)(?:\s+.*)?$"
            ),
            "setval": "configure generic-pon ont {{ 'no ' if sw_ver_mis_block == false else '' }}sw-ver-mis-block",
            "result": {
                "ont": {
                    "sw_ver_mis_block": "{{ False if negate else True }}",
                },
            },
        },
        {
            "name": "ont.sn_autounlock",
            "compval": "sn_autounlock",
            "getval": re.compile(
                r"^configure\sgeneric-pon\sont\s(?P<negate>no\s)?(?P<sn_autounlock>sn-autounlock)(?:\s+.*)?$"
            ),
            "setval": "configure generic-pon ont {{ 'no ' if sn_autounlock == false else '' }}sn-autounlock",
            "result": {
                "ont": {
                    "sn_autounlock": "{{ False if negate else True }}",
                },
            },
        },
        {
            "name": "alarmflag.ponlos_alarm_ctrl",
            "compval": "ponlos_alarm_ctrl",
            "getval": re.compile(
                r"^configure\sgeneric-pon\salarmflag\s(?P<negate>no\s)?(?P<ponlos_alarm_ctrl>ponlos-alarm-ctrl)(?:\s+.*)?$"
            ),
            "setval": "configure generic-pon alarmflag {{ 'no ' if ponlos_alarm_ctrl == false else '' }}ponlos-alarm-ctrl",
            "result": {
                "alarmflag": {
                    "ponlos_alarm_ctrl": "{{ False if negate else True }}",
                },
            },
        },
    ]
    # fmt: on
