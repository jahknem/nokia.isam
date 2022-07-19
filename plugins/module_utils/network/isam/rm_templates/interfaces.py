# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

import debugpy

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
        if not(debugpy.is_client_connected()):
            debugpy.listen(3000)
            debugpy.wait_for_client()       
            debugpy.breakpoint()
        super(InterfacesTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "key_a",
            "getval": re.compile(
                r"""
                ^port\s(?P<name>\S+)
                \s+(?P<adminup>no admin-up|admin-up)
                \s+(?P<linkupdowntrap>no link-updown-trap|link-updown-trap)
                \s+(?P<user>no user|user \S+)
                \s+(?P<severity>no severity|severity \S+)
                \s+(?P<porttype>no port-type|port-type \S+)\s+
                $""", re.VERBOSE),
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
    ]
    # fmt: on
