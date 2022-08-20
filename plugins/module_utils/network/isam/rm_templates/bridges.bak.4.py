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
                "ageing_time": "{{ 'None' if negate_ageing_time is defined else ageing_time|string }}",
            },
        },
        {
            "name": "bridge_port_default_priority",
            "getval": re.compile(
                r"""configure\sbridge\sport\s(?P<id>\S+)\s(?P<negate_default_priority>no\sdefault-priority)|(?P<default_priority>default-priority)""", re.VERBOSE),
            "setval": "",
            "result": {
#                "bridges": {
                    "{{ id }}": {
                        "default-priority": "{{ 3 if negate_default_priority is defined else default_priority|int }}",
                    },
#                },
            },
        },
        {
            "name": "bridge_port_mac_learn_off",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\s
                (?P<negate_mac_learn_off>no mac-learn-off)|(?P<mac_learn_off>mac-learn-off)
                """, re.VERBOSE),
            "setval": "",
            "result": {
#                "bridges": {
                    "{{ id }}": {
                        "mac-learn-off": "{{ False if negate_mac_learn_off is defined and mac_learn_off is not defined else True }}",
                    },
#                },
            },
        },
        {
            "name": "bridge_port_max_unicast_mac",
            "getval": re.compile(
                r"""
                configure\sbridge\sport\s(?P<id>\S+)\s
                (?P<negate_max_unicast_mac>no max-unicast-mac)|(max-unicast-mac (?P<max_unicast_mac>\d))
                """, re.VERBOSE),
            "setval": "",
            "result": {
#                "bridges": {
                    "{{ id }}": {
                        "max-unicast-mac": "{{ 1 if negate_max_unicast_mac is defined else max_unicast_mac|int }}",
                    },
#                },
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
#                "bridges": {
                    "{{ id }}": {
                        "vlan_tpid0": {
                            "id": "{{ vlan_tpid0|int }}",
                            "tpid": "{{ '0' if negate_tpid is defined else tpid|int }}",
                        },
                    },
#                },
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
#                "bridges": {
                    "{{ id }}": {
                        "vlan_tpid1": {
                            "id": "{{ vlan_tpid1|int }}",
                            "tpid": "{{ '0' if negate_tpid is defined else tpid|int }}",
                        },
                    },
#                },
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
#                "bridges": {
                    "{{ id }}": {
                        "pvid": "{{ None if negate_pvid is defined else pvid|String }}",
                    },
#                },
            },
        },
    ]
    # fmt: on
