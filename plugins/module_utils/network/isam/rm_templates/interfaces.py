# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The Interfaces parser templates file. This contains
a list of parser definitions and associated functions that
facilitates both facts gathering and native command generation for
the given network resource.
"""

import re
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)

class InterfacesTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(InterfacesTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            'name': 'name',
            'getval': re.compile(
                r'''port\s+(?P<id>(xdsl-line:|vlan-port|ethernet-line|atm-bonding|bonding|ip-gateway|ip-line|shdsl-line|ima-group|vlan-port|pon|ont|uni|voip|epon|eont|ellid|euni|la-group)\S+)''', re.VERBOSE,
            ),
            'setval': 'configure interface port {{ name }}',
            'result': {
                '{{ id }}': {
                    'name': '{{ id }}',
                },
            },
            'shared': True,
        },
        {
            'name': 'admin_up',
            'getval': re.compile(
                r'''\s+(?P<negate> no)?\s(?P<adminup>admin-up)''', re.VERBOSE,
            ),
            'setval': 'configure interface port {{ name }} {{ "no" if admin_up == false }} admin-up',
            'result': {
                '{{ id }}': {
                    'admin_up': '{{ True if adminup is defined and negate is not defined else False }}',
                },
            },
        },
        {
            'name': 'link_updown_trap',
            'getval': re.compile(
                r'''\s+(?P<negate> no)?\s(?P<linkupdowntrap>link-updown-trap)''', re.VERBOSE,
            ),
            'setval': 'configure interface port {{ name }} {{ "no" if link_updown_trap == false }} link-updown-trap',
            'result': {
                '{{ id }}': {
                    'link_updown_trap': '{{ True if linkupdowntrap is defined and negate is not defined else False }}',
                },
            },
        },
        {
            'name': 'user',
            'getval': re.compile(r'''\s+(?P<negate> no)?\s+user\s(?:"(?P<user_quoted>[^"]*)"|(?P<user>[^\s]+))''', re.VERBOSE,),
            'setval': 'configure interface port {{ name }} user {{ user }}',
            'result': {
                '{{ id }}': {
                    'user': '{{ "available" if negate is defined else (user_quoted|default(user)|string) }}',
                },
            },
        },
        {
            'name': 'severity',
            'getval': re.compile(
                r'''\s+(?P<negate> no)?\sseverity\s+(?P<severity>(indeterminate|warning|minor|major|critical|no-alarms|default|no-value|))''', re.VERBOSE,
            ),
            'setval': 'configure interface port {{ name }} severity {{ severity }}',
            'result': {
                '{{ id }}': {
                    'severity': '{{ "default" if negate is defined and severity is not defined else severity|string}}',
                },
            },
        },
        {
            'name': 'port_type',
            'getval': re.compile(
                r'''\s+(?P<negate> no)?\sport-type\s(?P<port_type>uni|nni|hc-uni|uplink|)?$''', re.VERBOSE,
            ),
            'setval': 'configure interface port {{ name }} port-type {{ port_type }}',
            'result': {
                '{{ id }}': {
                    'port_type': '{{ "uni" if negate is defined and port_type is not defined else port_type|string}}',
                },
            },
        },
    ]
    # fmt: on
