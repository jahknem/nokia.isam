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
            'name': 'id',
            'getval': re.compile(
                r'''
                port\s+(?P<id>(xdsl-line:|vlan-port|ethernet-line|atm-bonding|bonding|ip-gateway|ip-line|shdsl-line|ima-group|vlan-port|pon|ont|uni|voip|epon|eont|ellid|euni|la-group)\S+)
                $''', re.VERBOSE,
            ),
            'setval': 'port {{ name }}',
            'result': {
                '{{ name }}': {
                    'name': '{{ name }}',
                },
            },
        },
        {
            'name': 'admin-up',
            'getval': re.compile(
                r'''
                (?P<negate>\sno)?\s(?P<adminup>admin-up)
                $''', re.VERBOSE,
            ),
            'setval': 'description {{ description }}',
            'result': {
                '{{ name }}': 
                {                    
                    'admin-up': '{{ True if adminup is defined and negate is not defined else False }}',
                },
            },
        },
        {
            'name': 'link-updown-trap',
            'getval': re.compile(
                r'''
                (?P<negate>\sno)?\s(?P<linkupdowntrap>link-updown-trap)
                $''', re.VERBOSE,
            ),
            'setval': 'description {{ description }}',
            'result': {
                '{{ name }}': {
                    'link-up-down-trap': '{{ True if link-updown-trap is defined and negate is not defined else False }}',
                },
            },
        },
        {
            'name': 'user',
            'getval': re.compile(
                r'''
                (?P<negate>\sno)?\s+(user\s+(?P<user>[a-zA-Z0-9_]*))
                $''', re.VERBOSE,
            ),
            'setval': 'description {{ description }}',
            'result': {
                '{{ name }}': {
                    'user': '{{ "available" if negate is defined and user is not defined else user|string}}',
                },
            },
        },
        {
            'name': 'severity',
            'getval': re.compile(
                r'''
                (?P<negate>\sno)?\sseverity\s+(?P<severity>(indeterminate|warning|minor|major|critical|no-alarms|default|no-value))?
                $''', re.VERBOSE,
            ),
            'setval': 'description {{ description }}',
            'result': {
                '{{ name }}': {
                    'severity': '{{ "default" if negate is defined and severity is not defined else severity|string}}',
                },
            },
        },
        {
            'name': 'port-type',
            'getval': re.compile(
                r'''
                (?P<negate>\sno)?\sport-type\s(?P<porttype>uni|nni|hc-uni|uplink)?
                $''', re.VERBOSE,
            ),
            'setval': 'description {{ description }}',
            'result': {
                '{{ name }}': {
                    'port-type': '{{ "uni" if negate is defined and porttype is not defined else port-type|string}}',
                },
            },
        },
    ]
    # fmt: on
