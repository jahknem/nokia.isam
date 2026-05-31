# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Li_vlanTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Li_vlanTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "vlan_id",
            "getval": re.compile(
                r"""
                ^configure\sli_vlan\svlan-id\s(?P<vlan_id>\d+)
                $""", re.VERBOSE),
            "setval": "configure li_vlan vlan-id {{ vlan_id }}",
            "result": {
                "vlan_id": "{{ vlan_id|int }}",
            },
        },
    ]
    # fmt: on
