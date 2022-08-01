# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The Vlans parser templates file. This contains
a list of parser definitions and associated functions that
facilitates both facts gathering and native command generation for
the given network resource.
"""

import re
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)

class VlansTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(VlansTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            'name': 'id',
            'getval': re.compile(
                r'''
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
            'shared': True,
        },
        {
            'name': 'name',
            'getval': re.compile(
                r'''
                (?P<negate> no)?\s+(name\s+(?P<name>[a-zA-Z0-9_]*))
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'mode',
            'getval': re.compile(
                r'''
                (mode\s+(?P<user>(cross-connect|residential-bridge|qos-aware|layer2-terminated|mirror))
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'sntp-proxy',
            'getval': re.compile(
                r'''
                (?P<negate> no)?\s(?P<sntp_proxy>sntp-proxy)
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'priority',
            'getval': re.compile(
                r'''
                (?P<negate> no)?\spriority\s(?P<priority>\d)
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'vmac-not-in-opt61',
            'getval': re.compile(
                r'''
                (?P<negate> no)?\s(?P<vmac_not_in_opt61>vmac-not-in-opt61)
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'new-broadcast',
            'getval': re.compile(
                r'''
                (?P<negate> no)?\s+(new-broadcast\s+(?P<new_broadcast>(inherit|disable|enable)))
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'protocol-filter',
            'getval': re.compile(
                r'''
                (?P<negate> no)?\s+(protocol-filter\s+(?P<new_broadcast>(pass-all|pass-pppoe|pass-ipoe|pass-pppoe-ipoe|pass-ipv6oe|pass-pppoe-ipv6oe|pass-ipoe-ipv6oe|pass-pppoe-ipoe-ipv6oe)))
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'pppoe-relay-tag',
            'getval': re.compile(
                r'''
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'drly-srv-usr-side',
            'getval': re.compile(
                r'''
                (?P<negate> no)?\s(?P<drly_srv_usr_side>drly-srv-usr-side)
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'new-secure-fwd',
            'getval': re.compile(
                r'''
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'aging-time',
            'getval': re.compile(
                r'''
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'l2cp-transparent',
            'getval': re.compile(
                r'''
                (?P<negate> no)?\s(?P<l2cp_transparent>l2cp-transparent)
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'in-qos-prof-name',
            'getval': re.compile(
                r'''
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'ipv4-mcast-ctrl',
            'getval': re.compile(
                r'''
                (?P<negate> no)?\s(?P<ipv4_mcast_ctrl>ipv4-mcast-ctrl)
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'ipv6-mcast-ctrl',
            'getval': re.compile(
                r'''
                (?P<negate> no)?\s(?P<ipv6_mcast_ctrl>ipv6-mcast-ctrl)
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'mac-mcast-ctrl',
            'getval': re.compile(
                r'''
                (?P<negate> no)?\s(?P<mac_mcast_ctrl>mac-mcast-ctrl)
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'dis-proto-rip',
            'getval': re.compile(
                r'''
                (?P<negate> no)?\s(?P<dis_proto_rip>dis-proto-rip)
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'proto-ntp',
            'getval': re.compile(
                r'''
                (?P<negate> no)?\s(?P<proto_ntp>proto-ntp)
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'dis-ip-antispoof',
            'getval': re.compile(
                r'''
                (?P<negate> no)?\s(?P<dis_ip_antispoof>dis-ip-antispoof)
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'unknown-unicast',
            'getval': re.compile(
                r'''
                (?P<negate> no)?\s(?P<unknown_unicast>unknown-unicast)
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'pt2ptgem-flooding',
            'getval': re.compile(
                r'''
                (?P<negate> no)?\s(?P<pt2ptgem_flooding>pt2ptgem-flooding)
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'mac-movement-ctrl',
            'getval': re.compile(
                r'''
                (?P<negate> no)?\s(?P<mac_movement_ctrl>mac-movement-ctrl)
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'cvlan4095passthru',
            'getval': re.compile(
                r'''
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'arp-snooping',
            'getval': re.compile(
                r'''
                (?P<negate> no)?\s(?P<arp_snooping>arp-snooping)
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'arp-polling',
            'getval': re.compile(
                r'''
                (?P<negate> no)?\s(?P<arp_polling>arp-polling)
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'arp-polling-ip',
            'getval': re.compile(
                r'''
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
        {
            'name': 'mac-unauth',
            'getval': re.compile(
                r'''
                (?P<negate> no)?\s(?P<mac_unauth>mac-unauth)
                $''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ name }}': {
                    'id': '{{ name }}',
                },
            },
        },
    ]
    # fmt: on
