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
        super(BridgesTemplate, self).__init__(
            lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "ageing_time",
            "getval": re.compile(
                r"""
                ^configure\sbridge\s(?P<negate_ageing_time>no\sageing-time)|(ageing-time\s(?P<ageing_time>\S+))$
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "ageing_time": "{{ 300 if negate_ageing_time is defined else ageing_time|int }}",
            },
        },
        {
            "name": "bridge_port",
            "getval": re.compile(
                r"""
                ^configure\sbridge\sport\s(?P<id>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}":
                    {}
                },
            },
        },
        {
            "name": "default_priority",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\s(?P<negate_default_priority>no\sdefault-priority)|(?P<default_priority>default-priority)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "default_priority": "{{ 0 if negate_default_priority is defined and default_priority is not defined else default_priority|int }}",
                    },
                },
            },
        },
        {
            "name": "mac_learn_off",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\s(?P<negate_mac_learn_off>no\smac-learn-off)|(?P<mac_learn_off>mac-learn-off)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "mac_learn_off": "{{ False if negate_mac_learn_off is defined else True }}",
                    },
                },
            },
        },
        {
            "name": "max_unicast_mac",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\s((?P<negate_max_unicast_mac>no max-unicast-mac)|(max-unicast-mac (?P<max_unicast_mac>\d)))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "max_unicast_mac": "{{ None if negate_max_unicast_mac is defined else max_unicast_mac|int }}",
                    },
                },
            },
        },
        {
            "name": "qos_profile",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\s((?P<negate_qos_profile>no\sqos-profile)|(qos-profile\s(?P<qos_profile>\S+)))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "qos_profile": "{{ none if negate is defined else qos_profile|string }}",
                    },
                },
            },
        },
        {
            "name": "prio_regen_prof",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\s((?P<negate_prio_regen_prof>no\sprio-regen-prof)|(prio-regen-prof\s(?P<prio_regen_prof>\S+)))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "prio_regen_prof": "{{ none if negate is defined else prio_regen_prof|string }}",
                    },
                },
            },
        },
        {
            "name": "prio_regen_name",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\s(?P<negate_prio_regen_name>no\sprio-regen-name)|(prio-regen-name(?P<prio_regen_name>(none|trusted-port|best-effort|cl-all-prio-3|cl-all-prio-4|background|be-cl-voice|be-cl-ld-voice|be-voice|l2-vpn-3|l2-vpn-4|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31|32)))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "prio_regen_name": "{{ none if negate_prio_regen_name is defined else prio_regen_name|string }}",
                    },
                },
            },
        },
        {
            "name": "max_comitted_mac",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\s(?P<negate_max_comitted_mac>no\smax-committed-mac)|(max-committed-mac\s(?P<max_comitted_mac>(\d+)))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "max_comitted_mac": "{{ none if negate_max_comitted_mac is defined else max_comitted_mac|int }}",
                    },
                },
            },
        },
        {
            "name": "mirror_mode",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\s(?P<negate_mirror_mode>no\smirror-mode)|(mirror-mode\s(?P<mirror_mode>\S+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "mirror_mode": "{{ none if negate_mirror_mode is defined else mirror_mode|string }}",
                    },
                },
            },
        },
        {
            "name": "mirror_vlan",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\s(?P<negate_mirror_vlan>no\smirror-vlan)|(mirror-vlan\s(?P<mirror_vlan>(\d+|\#)))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "mirror_vlan": "{{ none if negate is defined else mirror_vlan|int }}",
                    },
                },
            },
        },
        {
            "name": "pvid_tagging_flag",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\s(?P<negate_pvid_tagging_flag>no\spvid-tagging-flag)|(pvid-tagging-flag\s(?P<pvid_tagging_flag>\S+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "pvid_tagging_flag": "{{ none if negate_pvid_tagging_flag is defined else pvid_tagging_flag|string }}",
                    },
                },
            },
        },
        {
            "name": "ds_pbit_mode",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\s(?P<negate_ds_pbit_mode>no\sds-pbit-mode)|(ds-pbit-mode\s(?P<ds_pbit_mode>\S+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "ds_pbit_mode": "{{ none if negate_ds_pbit_mode is defined else ds_pbit_mode|string }}",
                    },
                },
            },
        },
        {
            "name": "vlan_id",
            "getval": re.compile(
                r"""
                ^configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<vlan_id>(\S+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}":
                            {}
                        },
                    },
                },
            },
        },
        {
            "name": "tag",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<vlan_id>(\S+))\s(?P<negate_tag>no\stag)|(tag\s(?P<tag>\S+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}": {
                                "tag": "{{ none if negate_tag is defined else tag|string }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "l2fwder_vlan",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<vlan_id>(\S+))(?P<negate_l2fwder_vlan>nol2fwder-vlan)|(l2fwder-vlan\s(?P<l2fwder_vlan>\d+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}": {
                                "l2fwder_vlan": "{{ none if negate_l2fwder_vlan is defined else l2fwder_vlan|string }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "vlan_scope",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<negate_vlan_scope>no\svlan-scope)|(vlan-scope\s(?P<vlan_scope>\S+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}": {
                                "vlan_scope": "{{ none if negate_vlan_scope is defined else vlan_scope|string }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "qos",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<negate_qos>no qos)|(qos\s(?P<qos>\S+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}": {
                                "qos": "{{ none if negate_qos is defined else qos|string }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "qos_profile",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<negate_qos_profile>no qos-profile)|(qos-profile\s(?P<qos_profile>\S+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}": {
                                "qos_profile": "{{ none if negate_qos_profile is defined else qos_profile|string }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "prior_best_effort",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<negate_prior_best_effort>no\sprior-best-effort)|(prior-best-effort\s(?P<prior_best_effort>\S+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}": {
                                "prior_best_effort": "{{ none if negate_prior_best_effort is defined else True }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "prior_background",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<negate_prior_background>no\sprior-background)|(prior-background\s(?P<prior_background>\S+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}": {
                                "prior_background": "{{ none if negate_prior_background is defined else True }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "prior_spare",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<negate_prior_spare>no\sprior-spar)|(prior-spare\s(?P<prior_spare>\S+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}": {
                                "prior_spare": "{{ none if negate_prior_spare is defined else True }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "prior_exc_effort",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<negate_prior_exc_effort>no\sprior-exc-effort)|(prior-exc-effort\s(?P<prior_exc_effort>\S+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}": {
                                "prior_exc_effort": "{{ none if negate_prior_exc_effort is defined else True }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "prior_ctrl_load",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<negate_prior_ctrl_load>no\sprior-ctrl-load)|(prior-ctrl-load\s(?P<prior_ctrl_load>\S+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}": {
                                "prior_ctrl_load": "{{ none if negate_prior_ctrl_load is defined else True }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "prior_less_100ms",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<negate_prior_less_100ms>no\sprior-less-100ms)|(prior-less-100ms\s(?P<prior_less_100ms>\S+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}": {
                                "prior_less_100ms": "{{ none if negate_prior_less_100ms is defined else True }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "prior_less_10ms",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<negate_prior_less_10ms>no\sprior-less-10ms)|(prior-less-10ms\s(?P<prior_less_10ms>\S+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}": {
                                "prior_less_10ms": "{{ none if negate_prior_less_10ms is defined else True }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "prior_nw_ctrl",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<negate_prior_nw_ctrl>no\sprior-nw-ctrl)|(prior-nw-ctrl\s(?P<prior_nw_ctrl>\S+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}": {
                                "prior_nw_ctrl": "{{ none if negate_prior_nw_ctrl is defined else True }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "in_qos_prof_name",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<negate_in_qos_prof_name>no\sin-qos-prof-name)|(in-qos-prof-name\s(?P<in_qos_prof_name>\S+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}": {
                                "in_qos_prof_name": "{{ none if negate_in_qos_prof_name is defined else in_qos_prof_name|string }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "max_up_qos_policy",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<negate_max_up_qos_policy>no\smax-up-qos-policy)|(max-up-qos-policy\s(?P<max_up_qos_policy>(\d|\#)))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}": {
                                "max_up_qos_policy": "{{ 0 if negate is defined else max_up_qos_policy|int }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "max_ip_antispoof",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<negate_max_ip_antispoof>no\smax-ip-antispoof)|(max-ip-antispoof\s(?P<max_ip_antispoof>\S+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}": {
                                "max_ip_antispoof": "{{ 65535 if negate_max_ip_antispoof is defined else max_ip_antispoof|int }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "max_unicast_mac",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<negate_max_unicast_mac>no\smax-unicast-mac)|(max-unicast-mac\s(?P<max_unicast_mac>\S+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}": {
                                "max_unicast_mac": "{{ 65535 if negate is defined else max_unicast_mac|int }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "max_ipv6_antispf",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<negate_max_ipv6_antispf>no\smax-ipv6-antispf)|(max-ipv6-antispf\s(?P<max_ipv6_antispf>\S+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}": {
                                "max_ipv6_antispf": "{{ 65535 if negate_max_ipv6_antispf is defined else max_ipv6_antispf|int }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "mac_learn_ctrl",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<negate_mac_learn_ctrl>no\smac-learn-ctrl)|(mac-learn-ctrl\s(?P<mac_learn_ctrl>\S+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}": {
                                "mac_learn_ctrl": "{{ 3 if negate_mac_learn_ctrl is defined else mac_learn_ctrl|int }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "min_cvlan_id",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<negate_min_cvlan_id>no\smin-cvlan-id)|(min-cvlan-id\s(?P<min_cvlan_id>(\d+|\#)))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}": {
                                "min_cvlan_id": "{{ 1 if negate_min_cvlan_id is defined else min_cvlan_id|int }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "max_cvlan_id",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<negate_max_cvlan_id>no\smax-cvlan-id)|(max-cvlan-id\s(?P<max_cvlan_id>(\d+|\#)))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}": {
                                "max_cvlan_id": "{{ 4095 if negate_max_cvlan_id is defined else max_cvlan_id }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "ds_dedicated_q",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\svlan-id\s(?P<negate_ds_dedicated_q>no\sds-dedicated-q)|(ds-dedicated-q\s(?P<ds_dedicated_q>\S+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": {
                            "{{ vlan_id}}": {
                                "ds_dedicated_q": "{{ False if negate_ds_dedicated_q is defined else True }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "tpid",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+tpid\s(?P<tpid>[a-zA-Z0-9_]*)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {

                            "tpid": "{{ 0 if negate is defined else tpid|string }}",
                        }
                    }
                }
            },
        },
    ]
    # fmt: on
