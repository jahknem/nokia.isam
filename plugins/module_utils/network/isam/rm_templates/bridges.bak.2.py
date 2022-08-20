# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The Bridges parser templates file. This contains
a list of parser definitions and associated functions that
facilitates both facts gathering and native command generation for
the given network resource.
"""

import re
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)

class BridgesTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(BridgesTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "ageing_time",
            "getval": re.compile(
                r"""
                ^configure\sbridge\s(?P<negate_ageing_time>no\sageing-time)|(ageing-time\s(?P<ageing_time>\S+))$
                """, re.VERBOSE),
            "setval": "",
            "result": {
                "ageing_time": "{{ None if negate_ageing_time is defined else ageing_time|int }}",
            },
        },
        {
            "name": "bridge_port",
            "getval": re.compile(
            r"""
            configure\sbridge\sport\s(?P<id>\S+)\s
            ((?P<negate_default_priority>no default-priority)\s?)?((?P<default_priority>default-priority)\s?)?
            ((?P<negate_mac_learn_off>no mac-learn-off)\s?)?((?P<mac_learn_off>mac-learn-off)\s?)?
            ((?P<negate_max_unicast_mac>no max-unicast-mac)\s?)?(max-unicast-mac (?P<max_unicast_mac>\d)\s?)?
            ((?P<negate_qos_profile>no qos-profile)\s?)?(qos-profile (?P<qos_profile>\S+)\s?)?
            ((?P<negate_prio_regen_prof>no prio-regen-prof)\s?)?(prio-regen-prof (?P<prio_regen_prof>\S+)\s?)?
            ((?P<negate_prio_regen_name>no prio-regen-name)\s?)?(prio-regen-name (?P<prio_regen_name>\S+)\s?)?
            ((?P<negate_max_comitted_mac>no max-committed-mac)\s?)?(max-committed-mac (?P<max_committed_mac>\d+)\s?)?
            ((?P<negate_mirror_mode>no mirror-mode)\s?)?(mirror-mode (?P<mirror_mode>\S+)\s?)?
            ((?P<negate_mirror_vlan>no mirror-vlan)\s?)?(mirror-vlan (?P<mirror_vlan>\d+)\s?)?
            ((?P<negate_outervlancapture>no outervlancapture)\s?)?(outervlancapture (?P<outervlancapture>\d+)\s?)?
            ((?P<negate_direction>no direction)\s?)?(direction ((?P<direction>\d+)\s?))?
            ((?P<negate_pvid_tagging_flag>no pvid-tagging-flag)\s?)?(pvid-tagging-flag (?P<pvid_tagging_flag>\d+)\s?)?
            ((?P<negate_ds_pbit_mode>no ds-pbit-mode)\s?)?(ds-pbit-mode (?P<ds_pbit_mode>\d+)\s?)?
            ((?P<negate_default_tpid>no default-tpid)\s?)?(default-tpid (?P<default_tpid>\d+)\s?)?
            """, re.VERBOSE),
            "setval": "",
            "result": {
                "{{ id }}": {
                    "default-priority": "{{ 0 if negate_default_priority is defined else default_priority|int }}",
                    "mac-learn-off": "{{ False if negate_mac_learn_off is defined and mac_learn_off is not defined else True }}",
                    "max-unicast-mac": "{{ 1 if negate_max_unicast_mac is defined else max_unicast_mac|int }}",
                    "qos-profile": "{{ 'None' if negate_qos_profile is defined else qos_profile|string }}",
                    "prio-regen-prof": "{{ 'None' if negate_prio_regen_prof is defined else prio_regen_prof|string }}",
                    "prio-regen-name": "{{ 'None' if negate_prio_regen_name is defined else prio_regen_name|string }}",
                    "max-committed-mac": "{{ 65535 if negate_max_comitted_mac is defined else max_committed_mac|int }}",
                    "mirror-mode": "{{ 'disable' if negate_mirror_mode is defined else mirror_mode|string }}",
                    "mirror-vlan": "{{ 0 if negate_mirror_vlan is defined else mirror_vlan|int }}",
                    "outervlancapture": "{{ 0 if negate_outervlancapture is defined else outervlancapture|int }}",
                    "direction": "{{ 'bidirection' if negate_direction is defined else direction|string }}",
                    "pvid-tagging-flag": "{{ 'onu' if negate_pvid_tagging_flag is defined else pvid_tagging_flag|string }}",
                    "ds-pbit-mode": "{{ 'auto' if negate_ds_pbit_mode is defined else ds_pbit_mode|string }}",
                    "default-tpid": "{{ 8100 if negate_default_tpid is defined else default_tpid|int }}",
                }
            },
        },
        {
            "name": "vlan-tpid0",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-tpid0\s(?P<vlan_tpid0>\d+)
                (?P<negate_tpid>no tpid )?(tpid (?P<tpid>\S+))?
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "{{ id }}": {
                    "vlan_tpid0": {
                        "id": "{{ vlan_tpid0|int }}",
                        "tpid": "{{ '0' if negate_tpid is defined else tpid|int }}",
                    },
                },
            },
        },
        {
            "name": "vlan-tpid1",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-tpid1\s(?P<vlan_tpid1>\d+)
                (?P<negate_tpid>no tpid )?(tpid (?P<tpid>\S+))?
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "{{ id }}": {
                    "vlan_tpid1": {
                        "id": "{{ vlan_tpid1|int }}",
                        "tpid": "{{ '0' if negate_tpid is defined else tpid|int }}",
                    },
                },
            },
        },
        {
            "name": "vlan-id",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\s
                vlan-id (?P<vlan_id>\d+)\s
                ((?P<negate_tag>no tag)\s?)?(tag\s(?P<tag>\S+)\s?)?
                ((?P<negate_l2fwder_vlan>no l2fwder-vlan)\s?)?(l2fwder-vlan\s(?P<l2fwder_vlan>\S+)\s?)?
                ((?P<negate_vlan_scope>no vlan-scope)\s?)?(vlan-scope\s(?P<vlan_scope>\S+)\s?)?
                ((?P<negate_qos>no qos)\s?)?(qos\s(?P<qos>\S+)\s?)?
                ((?P<negate_qos_profile>no qos-profile)\s?)?(qos-profile\s(?P<qos_profile>\S+)\s?)?
                ((?P<negate_prior_best_effort>no prior-best-effort)\s?)?((?P<prior_best_effort>prior-best-effort)\s?)?
                ((?P<negate_prior_background>no prior-background)\s?)?((?P<prior_background>prior-background)\s?)?
                ((?P<negate_prior_spare>no prior-spare)\s?)?((?P<prior_spare>prior-spare)\s?)?
                ((?P<negate_prior_exc_effort>no prior-exc-effort)\s?)?((?P<prior_exc_effort>prior-exc-effort)\s?)?
                ((?P<negate_prior_ctrl_load>no prior-ctrl-load)\s?)?((?P<prior_ctrl_load>prior-ctrl-load)\s?)?
                ((?P<negate_prior_less_100ms>no prior-less-100ms)\s?)?((?P<prior_less_100ms>prior-less-100ms)\s?)?
                ((?P<negate_prior_less_10ms>no prior-less-10ms)\s?)?((?P<prior_less_10ms>prior-less-10ms)\s?)?
                ((?P<negate_prior_nw_ctrl>no prior-nw-ctrl)\s?)?((?P<prior_nw_ctrl>prior-nw-ctrl)\s?)?
                ((?P<negate_in_qos_prof_name>no in-qos-prof-name)\s?)?(in-qos-prof-name\s(?P<in_qos_prof_name>\S+)\s?)?
                ((?P<negate_max_up_qos_policy>no max-up-qos-policy)\s?)?(max-up-qos-policy\s(?P<max_up_qos_policy>\d+)\s?)?
                ((?P<negate_max_ip_antispoof>no max-ip-antispoof)\s?)?(max-ip-antispoof\s(?P<max_ip_antispoof>\d+)\s?)?
                ((?P<negate_max_unicast_mac>no max-unicast-mac)\s?)?(max-unicast-mac\s(?P<max_unicast_mac>\d+)\s?)?
                ((?P<negate_max_ipv6_antispf>no max-ipv6-antispf)\s?)?(max-ipv6-antispf\s(?P<max_ipv6_antispf>\d+)\s?)?
                ((?P<negate_mac_learn_ctrl>no mac-learn-ctrl)\s?)?(mac-learn-ctrl\s(?P<mac_learn_ctrl>\d+)\s?)?
                ((?P<negate_min_cvlan_id>no min-cvlan-id)\s?)?(min-cvlan-id\s(?P<min_cvlan_id>\d+)\s?)?
                ((?P<negate_max_cvlan_id>no max-cvlan-id)\s?)?(max-cvlan-id\s(?P<max_cvlan_id>\d+)\s?)?
                ((?P<negate_ds_dedicated_q>no ds-dedicated-q)\s?)?((?P<ds_dedicated_q>ds-dedicated-q)\s?)?
                ((?P<negate_tpid>no tpid)\s)?(tpid\s(?P<tpid>\S+)\s?)?
                ((?P<negate_inner_pbit_remark>no inner-pbit-remark)\s?)?(inner-pbit-remark\s(?P<inner_pbit_remark>\S+)\s?)?
                ((?P<negate_groupid>no groupid)\s?)?(groupid\s(?P<groupid>\d+)\s?)?
                ((?P<negate_usacceptframetype>no usacceptframetype)\s?)?(usacceptframetype\s(?P<usacceptframetype>\S+)\s?)?
                ((?P<negate_oltregenprofile>no oltregenprofile)\s?)?((?P<oltregenprofile>oltregenprofile)\s?)?
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "vlan": {
                    "{{ vlan_id }}": {
                        "tag": "{{ 'untagged' if negate_tag is defined else tag|string }}",
                        "l2fwder_vlan": "{{ 'stacked : 0 : 4097' if negate_l2fwder_vlan is defined else l2fwder_vlan|string }}",
                        "vlan_scope": "{{ 'l2fwder' if negate_vlan_scope is defined else vlan_scope|string }}",
                        "qos": "{{ 'profile:none' if negate_qos is defined else qos|string }}",
                        "qos_profile": "{{ 'none' if negate_qos_profile is defined else qos_profile|string }}",
                        "prior_best_effort": "{{ False if negate_prior_best_effort is defined else True }}",
                        "prior_background": "{{ False if negate_prior_background is defined else True }}",
                        "prior_spare": "{{ False if negate_prior_spare is defined else True }}",
                        "prior_exc_effort": "{{ False if negate_prior_exc_effort is defined else True }}",
                        "prior_ctrl_load": "{{ False if negate_prior_ctrl_load is defined else True }}",
                        "prior_less_100ms": "{{ False if negate_prior_less_100ms is defined else True }}",
                        "prior_less_10ms": "{{ False if negate_prior_less_10ms is defined else True }}",
                        "prior_nw_ctrl": "{{ False if negate_prior_nw_ctrl is defined else True }}",
                        "in_qos_prof_name": "{{ 'name:Default_TC0' if negate_in_qos_prof_name is defined else in_qos_prof_name|string }}",
                        "max_up_qos_policy": "{{ '0' if negate_max_up_qos_policy is defined else max_up_qos_policy|int }}",
                        "max_ip_antispoof": "{{ '65535' if negate_max_ip_antispoof is defined else max_ip_antispoof|int }}",
                        "max_unicast_mac": "{{ '65535' if negate_max_unicast_mac is defined else max_unicast_mac|int }}",
                        "max_ipv6_antispf": "{{ '65535' if negate_max_ipv6_antispf is defined else max_ipv6_antispf|int }}",
                        "mac_learn_ctrl": "{{ '3' if negate_mac_learn_ctrl is defined else mac_learn_ctrl|int }}",
                        "min_cvlan_id": "{{ '1' if negate_min_cvlan_id is defined else min_cvlan_id|int }}",
                        "max_cvlan_id": "{{ '4095' if negate_max_cvlan_id is defined else max_cvlan_id|int }}",
                        "ds_dedicated_q": "{{ False if negate_ds_dedicated_q is defined else True }}",
                        "tpid": "{{ '0' if negate_tpid is defined else tpid|string }}",
                        "inner_pbit_remark": "{{ 'untouched' if negate_inner_pbit_remark is defined else inner_pbit_remark|string }}",
                        "groupid": "{{ '0' if negate_groupid is defined else groupid|int }}",
                        "usacceptframetype": "{{ 'all' if negate_usacceptframetype is defined else usacceptframetype|string }}",
                        "oltregenprofile": "{{ 'disabled' if negate_oltregenprofile is defined else oltregenprofile|string }}",
                    },
                },
            },
        },
        {
            "name": "pvid",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\s
                ((?P<negate_pvid>no pvid))|(pvid\s(?P<pvid>\S+)s?)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "{{ id }}": {
                    "pvid": "{{ None if negate_pvid is defined else pvid|String }}",
                },
            },
        },
    ]
    # fmt: on
