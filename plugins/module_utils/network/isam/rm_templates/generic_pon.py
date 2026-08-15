# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re
from typing import Any, Dict

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    parse_cli_fields,
    parse_cli_key_values,
)


GENERIC_PON_FLAG_FIELDS = (
    "pon-pmcollect",
    "ont-pmcollect",
    "ontbulk-pmcollect",
    "slid-mode",
    "sn-bundle-timer",
    "sw-ver-mis-block",
    "sn-autounlock",
    "ponlos-alarm-ctrl",
)


class Generic_ponTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Generic_ponTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    def parse(self):
        result: Dict[str, Any] = {}
        for raw_line in self._lines or []:
            tokens = raw_line.strip().split()
            if tokens[:3] == ["configure", "generic-pon", "dpinteg-threshold"] and len(tokens) >= 4:
                result["dpinteg_threshold"] = int(tokens[3])
            elif tokens[:3] == ["configure", "generic-pon", "utilization"] and len(tokens) >= 4:
                section = result.setdefault("utilization", {})
                if tokens[3] == "threshold":
                    threshold = section.setdefault("threshold", {})
                    self._parse_pairs(tokens[4:], threshold)
                else:
                    self._parse_flags(tokens[3:], section)
            elif tokens[:3] == ["configure", "generic-pon", "ont"]:
                ont = result.setdefault("ont", {})
                self._parse_flags(tokens[3:], ont)
            elif tokens[:3] == ["configure", "generic-pon", "alarmflag"]:
                alarmflag = result.setdefault("alarmflag", {})
                self._parse_flags(tokens[3:], alarmflag)
        return result

    @staticmethod
    def _parse_pairs(tokens, target):
        target.update(parse_cli_key_values(tokens, negated_value=""))

    @classmethod
    def _parse_flags(cls, tokens, target):
        target.update(parse_cli_fields(tokens, bool_fields=GENERIC_PON_FLAG_FIELDS))

    # fmt: off
    PARSERS = [
        {
            "name": "dpinteg_threshold",
            "compval": "dpinteg_threshold",
            "getval": re.compile(
                r"^configure\sgeneric-pon\sdpinteg-threshold\s(?P<dpinteg_threshold>\S+)(?:\s+.*)?$"
            ),
            "setval": "configure generic-pon dpinteg-threshold {{ dpinteg_threshold }}",
            "remval": "configure generic-pon no dpinteg-threshold",
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


def _threshold_parser(field):
    return {
        "name": "utilization.threshold." + field,
        "compval": field,
        "getval": re.compile(
            r"^configure\sgeneric-pon\sutilization\sthreshold\s"
            r"(?:(?P<negate>no\s+)" + field + r"|" + field + r"\s+(?P<value>\S+))$"
        ),
        "setval": "configure generic-pon utilization threshold {{ 'no " + field + "' if " + field + " is none else '" + field + " ' + " + field + " }}",
        "remval": "configure generic-pon utilization threshold no " + field,
        "result": {
            "utilization": {
                "threshold": {
                    field: "{{ '' if negate is defined else value }}",
                }
            }
        },
    }


for _field in (
    "txmcutilhi", "txmcutilmd", "txmcutillo", "txtotutilhi", "txtotutilmd",
    "txtotutillo", "rxtotutilhi", "rxtotutilmd", "rxtotutillo", "dbacongperiodhi",
    "dbacongperiodmd", "dbacongperiodlo", "txucdropfrmhi", "txucdropfrmmd",
    "txucdropfrmlo", "txmcdropfrmhi", "txmcdropfrmmd", "txmcdropfrmlo",
    "txbcdropfrmhi", "txbcdropfrmmd", "txbcdropfrmlo", "rxtotdropfrmhi",
    "rxtotdropfrmmd", "rxtotdropfrmlo", "numtcint", "numtcintdba", "dbacongthresh",
):
    Generic_ponTemplate.PARSERS.append(_threshold_parser(_field))
