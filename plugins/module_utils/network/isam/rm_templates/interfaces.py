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
            "name": "key_a",
            "getval": re.compile(
                re.compile(r"""port\s(?P<name>(xdsl-line:|vlan-port|ethernet-line|atm-bonding|bonding|ip-gateway|ip-line|shdsl-line|ima-group|vlan-port|pon|ont|uni|voip|epon|eont|ellid|euni|la-group)\S+)[\S|\n]+\s+(?P<adminup>no admin-up|admin-up)[\S|\n]+\s+(?P<linkupdowntrap>no link-updown-trap|link-updown-trap)[\S|\n]+\s+(?P<user>no user|user \S+)( \# value=available|)[\S|\n]+\s+(?P<severity>no severity|severity \S+)( \# value=default|)[\S|\n]+\s+(?P<porttype>no port-type|port-type \S+)( \# value=uni|)[\S|\n]+exit$""", re.VERBOSE),
            "setval": "",
            "result": {
                "name": "{{ name }}",
                "admin-up": "{{ 'True' if adminup == 'admin-up' else 'False' }}",
                "link-state-trap": "no-value",
                "link-up-down-trap": "{{ 'True' if linkupdowntrap == 'link-updown-trap' else 'False' }}",
                "severity": "{{ 'no-value' if severity == 'no severity' or 'no severity # value=default' else severity }}",
                "port-type": "{{ 'no-value' if porttype == 'no port-type' or 'no port-type # value=uni' else porttype }}",
            },
            "shared": True
        },
        {
            "name": "id",
            "getval": re.compile(
                r"""
                (?P<name>(xdsl-line:|vlan-port|ethernet-line|atm-bonding|bonding|ip-gateway|ip-line|shdsl-line|ima-group|vlan-port|pon|ont|uni|voip|epon|eont|ellid|euni|la-group)\S+)
                $""", re.VERBOSE,
            ),
            "setval": "description {{ description }}",
            "result": {
                '{{ name }}': {
                    'name': '{{ name }}',
                },
            },
        },
        {
            "name": "admin-up",
            "getval": re.compile(
                r"""
                (?P<adminup>no admin-up|admin-up)
                $""", re.VERBOSE,
            ),
            "setval": "description {{ description }}",
            "result": {
                '{{ name }}': 
                {                    
                    'admin-up': '{{ True if adminup == "admin-up" else False }}',
                },
            },
        },
        {
            "name": "link-state-trap",
            "getval": re.compile(
                r"""
                (?P<linkupdowntrap>no link-updown-trap|link-updown-trap)
                $""", re.VERBOSE,
            ),
            "setval": "description {{ description }}",
            "result": {
                '{{ name }}': {
                    "link-state-trap": "no-value",
                },
            },
        },
        {
            "name": "link-state-trap",
            "getval": re.compile(
                r"""
                (?P<user>no user|user \S+)( \# value=available|)
                $""", re.VERBOSE,
            ),
            "setval": "description {{ description }}",
            "result": {
                '{{ name }}': {
                    "link-state-trap": "no-value",
                },
            },
        },
        {
            "name": "link-up-down-trap",
            "getval": re.compile(
                r"""
                (?P<linkupdowntrap>no link-updown-trap|link-updown-trap)
                $""", re.VERBOSE,
            ),
            "setval": "description {{ description }}",
            "result": {
                '{{ name }}': {
                    'link-up-down-trap': '{{ True if linkupdowntrap == link-updown-trap else False }}',
                },
            },
        },
        {
            "name": "severity",
            "getval": re.compile(
                r"""
                (?P<severity>no severity|severity \S+)( \# value=default|)
                $""", re.VERBOSE,
            ),
            "setval": "description {{ description }}",
            "result": {
                '{{ name }}': {
                    'severity': '{{ no-value if severity is {%no severity # value=default%} else severity }}',
                },
            },
        },
        {
            "name": "port-type",
            "getval": re.compile(
                r"""
                (?P<porttype>no port-type|port-type \S+)
                $""", re.VERBOSE,
            ),
            "setval": "description {{ description }}",
            "result": {
                '{{ name }}': {
                    'port-type': {{ 'no-value' if porttype is {%no port-type # value=uni%} else porttype }},
                },
            },
        },
    ]
    # fmt: on
