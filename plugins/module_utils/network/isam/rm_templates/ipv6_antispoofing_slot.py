# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import NetworkTemplate


class Isam_ipv6_antispoofing_slotTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Isam_ipv6_antispoofing_slotTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    PARSERS = [
        {
            "name": "bit_len",
            "compval": "bit_len",
            "getval": re.compile(r"^configure\s+ipv6-antispoofing\s+slot\s+(?P<name>\S+)\s+bit-len\s+(?P<bit_len>\d+)\s*$"),
            "setval": "configure ipv6-antispoofing slot {{ name }} bit-len {{ bit_len }}",
            "result": {"{{ name }}": {"name": "{{ name }}", "bit_len": "{{ bit_len | int }}"}},
        },
        {
            "name": "no_bit_len",
            "getval": re.compile(r"^configure\s+ipv6-antispoofing\s+slot\s+(?P<name>\S+)\s+no\s+bit-len\s*$"),
            "result": {"{{ name }}": {"name": "{{ name }}", "bit_len": 64}},
        },
    ]
