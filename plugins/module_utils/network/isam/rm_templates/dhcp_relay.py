# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Isam_dhcp_relayTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Isam_dhcp_relayTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "port_stats",
            "compval": "port_stats",
            "getval": re.compile(r"^configure\s+dhcp-relay\s+(?P<negate>no\s+)?port-stats\s+(?P<name>\S+)$"),
            "setval": "configure dhcp-relay {{ 'no ' if not port_stats else '' }}port-stats {{ name }}",
            "remval": "configure dhcp-relay no port-stats {{ name }}",
            "result": {"{{ name }}": {"name": "{{ name }}", "port_stats": "{{ False if negate is defined else True }}"}},
        },
        {
            "name": "v6_port_stats",
            "compval": "v6_port_stats",
            "getval": re.compile(r"^configure\s+dhcp-relay\s+(?P<negate>no\s+)?v6-port-stats\s+(?P<name>\S+)$"),
            "setval": "configure dhcp-relay {{ 'no ' if not v6_port_stats else '' }}v6-port-stats {{ name }}",
            "remval": "configure dhcp-relay no v6-port-stats {{ name }}",
            "result": {"{{ name }}": {"name": "{{ name }}", "v6_port_stats": "{{ False if negate is defined else True }}"}},
        },
    ]
    # fmt: on
