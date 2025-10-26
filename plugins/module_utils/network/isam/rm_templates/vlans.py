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
                r'''\bid\s+(?P<id>(?:\d+|stacked:\d+:\d+))''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                },
            },
            'shared': True,
        },
        {
            'name': 'id_with_mode',
            'getval': re.compile(
                r'''\bid\s+(?P<id>(?:\d+|stacked:\d+:\d+))\s+mode\s+(?P<mode>(cross-connect|residential-bridge|qos-aware|layer2-terminated|mirror))\s*$''',
                re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }} mode {{ mode }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    'mode': '{{ mode }}',
                },
            },
            'shared': True,
        },
        {
            'name': 'name',
            'getval': re.compile(
                r'''^\s+(?P<negate>no\s+)?name\s+(?:"(?P<name_quoted>[^"]+)"|(?P<name>[A-Za-z0-9_\-]+))\s*$''',
                re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    'name': '{{ name_quoted|default(name)|string }}',
                },
            },
        },
        {
            'name': 'mode',
            'getval': re.compile(
                r'''^\s+mode\s+(?P<mode>(cross-connect|residential-bridge|qos-aware|layer2-terminated|mirror))\s*$''',
                re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    'mode': '{{ mode }}',
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
                '{{ id }}': {
                    'id': '{{ id }}',
                },
            },
        },
        {
            'name': 'priority',
            'getval': re.compile(
                r'''^\s+(?P<negate>no\s+)?priority\s+(?P<priority>\d+)\s*$''',
                re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    'priority': '{{ priority|int }}',
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
                '{{ id }}': {
                    'id': '{{ id }}',
                },
            },
        },
        {
            'name': 'new-broadcast',
            'getval': re.compile(
                r'''^\s+(?:(?P<negate>no)\s+new-broadcast|(new-broadcast\s+(?P<new_broadcast>(inherit|disable|enable)))\s*)$''',
                re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    'new-broadcast': '{{ ("disable" if negate else new_broadcast)|default("inherit") }}',
                },
            },
        },
        {
            'name': 'protocol-filter',
            'getval': re.compile(
                r'''^\s+(?:(?P<negate>no)\s+protocol-filter|(protocol-filter\s+(?P<protocol_filter>(pass-all|pass-pppoe|pass-ipoe|pass-pppoe-ipoe|pass-ipv6oe|pass-pppoe-ipv6oe|pass-ipoe-ipv6oe|pass-pppoe-ipoe-ipv6oe)))\s*)$''',
                re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    'protocol-filter': '{{ ("pass-all" if negate else protocol_filter)|default("pass-all") }}',
                },
            },
        },
        {
            'name': 'pppoe-relay-tag',
            'getval': re.compile(
                r'''^\s+pppoe-relay-tag\s+(?P<pppoe_relay_tag>true|false|configurable)\s*$''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    'pppoe-relay-tag': '{{ pppoe_relay_tag }}',
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
                '{{ id }}': {
                    'id': '{{ id }}',
                },
            },
        },
        {
            'name': 'new-secure-fwd',
            'getval': re.compile(
                r'''^\s+new-secure-fwd\s+(?P<new_secure_fwd>(inherit|enable|disable))\s*$''',
                re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    'new-secure-fwd': '{{ new_secure_fwd }}',
                },
            },
        },
        {
            'name': 'aging-time',
            'getval': re.compile(
                r'''^\s+aging-time\s+(?P<aging_time>\d+)\s*$''',
                re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    'aging-time': '{{ aging_time|int }}',
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
                '{{ id }}': {
                    'id': '{{ id }}',
                },
            },
        },
        {
            'name': 'in-qos-prof-name',
            'getval': re.compile(
                r'''^\s+in-qos-prof-name\s+(?P<inqpn>\S+)\s*$''',
                re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    'in-qos-prof-name': '{{ inqpn|string }}',
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
                '{{ id }}': {
                    'id': '{{ id }}',
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
                '{{ id }}': {
                    'id': '{{ id }}',
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
                '{{ id }}': {
                    'id': '{{ id }}',
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
                '{{ id }}': {
                    'id': '{{ id }}',
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
                '{{ id }}': {
                    'id': '{{ id }}',
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
                '{{ id }}': {
                    'id': '{{ id }}',
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
                '{{ id }}': {
                    'id': '{{ id }}',
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
                '{{ id }}': {
                    'id': '{{ id }}',
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
                '{{ id }}': {
                    'id': '{{ id }}',
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
                '{{ id }}': {
                    'id': '{{ id }}',
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
                '{{ id }}': {
                    'id': '{{ id }}',
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
                '{{ id }}': {
                    'id': '{{ id }}',
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
                '{{ id }}': {
                    'id': '{{ id }}',
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
                '{{ id }}': {
                    'id': '{{ id }}',
                },
            },
        },
        # Additional DHCP/PPPoE and related options
        {
            'name': 'dhcp-opt82-ext',
            'getval': re.compile(
                r'''^\s+dhcp-opt82-ext\s+(?P<dhcp_opt82_ext>add-or-forward|enable)\s*$''',
                re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    'dhcp-opt82-ext': '{{ dhcp_opt82_ext }}',
                },
            },
        },
        {
            'name': 'dhcp-opt82-nni',
            'getval': re.compile(
                r'''^\s+dhcp-opt82-nni\s*$''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    'dhcp-opt82-nni': True,
                },
            },
        },
        {
            'name': 'dhcp-opt82-uplink',
            'getval': re.compile(
                r'''^\s+dhcp-opt82-uplink\s*$''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    'dhcp-opt82-uplink': True,
                },
            },
        },
        {
            'name': 'circuit-id-dhcp',
            'getval': re.compile(
                r'''^\s+circuit-id-dhcp\s+(?P<circuit_id_dhcp>physical-id)\s*$''',
                re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    'circuit-id-dhcp': '{{ circuit_id_dhcp }}',
                },
            },
        },
        {
            'name': 'remote-id-dhcp',
            'getval': re.compile(
                r'''^\s+remote-id-dhcp\s+(?P<remote_id_dhcp>customer-id)\s*$''',
                re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    'remote-id-dhcp': '{{ remote_id_dhcp }}',
                },
            },
        },
        {
            'name': 'relay-id-dhcp',
            'getval': re.compile(
                r'''^\s+relay-id-dhcp\s*$''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    'relay-id-dhcp': True,
                },
            },
        },
        {
            'name': 'linerates',
            'getval': re.compile(
                r'''^\s+(?P<lr>(?:dhcp|pppoe|dhcpv6)-linerate)\s*$''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    '{{ lr }}': True,
                },
            },
        },
        {
            'name': 'l2-encaps',
            'getval': re.compile(
                r'''^\s+(?P<l2>(?:pppoe|dhcp|dhcpv6)-l2-encaps|l2-encaps1)\s*$''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    '{{ l2 }}': True,
                },
            },
        },
        {
            'name': 'vlanaware',
            'getval': re.compile(
                r'''^\s+(?P<aware>(?:pppoer|dhcpr|dhcpv6r)-vlanaware)\s*$''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    '{{ aware }}': True,
                },
            },
        },
        {
            'name': 'circuit-id-pppoe',
            'getval': re.compile(
                r'''^\s+circuit-id-pppoe\s+(?P<circuit_id_pppoe>physical-id)\s*$''',
                re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    'circuit-id-pppoe': '{{ circuit_id_pppoe }}',
                },
            },
        },
        {
            'name': 'remote-id-pppoe',
            'getval': re.compile(
                r'''^\s+remote-id-pppoe\s+(?P<remote_id_pppoe>customer-id)\s*$''',
                re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    'remote-id-pppoe': '{{ remote_id_pppoe }}',
                },
            },
        },
        {
            'name': 'dhcpv6-identifiers',
            'getval': re.compile(
                r'''^\s+(?P<key>dhcpv6-(?:itf-id|remote-id))\s+(?P<val>physical-id|customer-id)\s*$''',
                re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    '{{ key }}': '{{ val }}',
                },
            },
        },
        {
            'name': 'dhcpv6-flags',
            'getval': re.compile(
                r'''^\s+(?P<key>dhcpv6-(?:relay-id|trst-port))\s*$''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    '{{ key }}': True,
                },
            },
        },
        {
            'name': 'enterprise-number',
            'getval': re.compile(
                r'''^\s+enterprise-number\s+(?P<enterprise_number>\d+)\s*$''',
                re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    'enterprise-number': '{{ enterprise_number|int }}',
                },
            },
        },
        {
            'name': 'icmpv6-sec-fltr',
            'getval': re.compile(
                r'''^\s+icmpv6-sec-fltr\s*$''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    'icmpv6-sec-fltr': True,
                },
            },
        },
        {
            'name': 'vmac-translation',
            'getval': re.compile(
                r'''^\s+vmac-translation\s*$''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    'vmac-translation': True,
                },
            },
        },
        {
            'name': 'vmac-dnstr-filter',
            'getval': re.compile(
                r'''^\s+vmac-dnstr-filter\s*$''', re.VERBOSE,
            ),
            'setval': 'configure vlan id {{ id }}',
            'result': {
                '{{ id }}': {
                    'id': '{{ id }}',
                    'vmac-dnstr-filter': True,
                },
            },
        },
    ]
    # fmt: on
