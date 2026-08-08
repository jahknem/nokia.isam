# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import NetworkTemplate


class Isam_arp_relayTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Isam_arp_relayTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    PARSERS = [
        {
            "name": "statistics",
            "compval": "statistics",
            "getval": re.compile(
                r"^configure\sarp-relay\sstatistics\s(?P<name>.+?)\s*$"
            ),
            "setval": "configure arp-relay statistics {{ name }}",
            "result": {
                "{{ name }}": {
                    "name": "{{ name }}",
                    "statistics": True,
                },
            },
            "shared": True,
        },
        {
            "name": "no_statistics",
            "getval": re.compile(
                r"^configure\sarp-relay\sno\sstatistics\s(?P<name>.+?)\s*$"
            ),
            "result": {
                "{{ name }}": {
                    "name": "{{ name }}",
                    "statistics": False,
                },
            },
            "shared": True,
        },
    ]
