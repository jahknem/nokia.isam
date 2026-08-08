# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Isam_dhcp_serverTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Isam_dhcp_serverTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "start_addr",
            "compval": "start_addr",
            "getval": re.compile(r"^configure\sdhcp-server\sstart-addr\s(?P<start_addr>\S+)$"),
            "setval": "configure dhcp-server start-addr {{ start_addr }}",
            "remval": "configure dhcp-server start-addr",
            "result": {
                "start_addr": "{{ start_addr }}",
            },
        },
        {
            "name": "end_addr",
            "compval": "end_addr",
            "getval": re.compile(r"^configure\sdhcp-server\send-addr\s(?P<end_addr>\S+)$"),
            "setval": "configure dhcp-server end-addr {{ end_addr }}",
            "remval": "configure dhcp-server end-addr",
            "result": {
                "end_addr": "{{ end_addr }}",
            },
        },
        {
            "name": "subnet_mask",
            "compval": "subnet_mask",
            "getval": re.compile(r"^configure\sdhcp-server\ssubnet-mask\s(?P<subnet_mask>\S+)$"),
            "setval": "configure dhcp-server subnet-mask {{ subnet_mask }}",
            "remval": "configure dhcp-server subnet-mask",
            "result": {
                "subnet_mask": "{{ subnet_mask }}",
            },
        },
        {
            "name": "lease_time",
            "compval": "lease_time",
            "getval": re.compile(r"^configure\sdhcp-server\slease-time\s(?P<lease_time>\d+)$"),
            "setval": "configure dhcp-server lease-time {{ lease_time }}",
            "remval": "configure dhcp-server lease-time",
            "result": {
                "lease_time": "{{ lease_time }}",
            },
        },
        {
            "name": "restart",
            "compval": "restart",
            "getval": re.compile(
                r"^configure\sdhcp-server\s(?P<negate_restart>no\s)?restart$"
            ),
            "setval": "configure dhcp-server {{ 'no ' if restart == false else '' }}restart",
            "result": {
                "restart": "{{ False if negate_restart else True }}",
            },
        },
        {
            "name": "dhcp_packed",
            "getval": re.compile(
                r"^configure\sdhcp-server\s"
                r"start-addr\s(?P<start_addr>\S+)\s+"
                r"(?:stop-addr|end-addr)\s(?P<end_addr>\S+)"
                r"(?:\s+subnet-mask\s(?P<subnet_mask>\S+))?"
                r"(?:\s+lease-time\s(?P<lease_time>\d+))?"
                r"(?:\s+(?P<negate_restart>no\s)?restart)?"
                r"(?:\s+.*)?$"
            ),
            "result": {
                "start_addr": "{{ start_addr }}",
                "end_addr": "{{ end_addr }}",
                "subnet_mask": "{{ subnet_mask|default('') }}",
                "lease_time": "{{ lease_time|default('') }}",
                "restart": "{{ False if negate_restart|default('') else True }}",
            },
        },
    ]
    # fmt: on
