# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Isam_systemTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Isam_systemTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "id.name",
            "compval": "name",
            "getval": re.compile(
                r"^configure\ssystem\sid\sname\s(?P<name>\S+)$"
            ),
            "setval": "configure system id name {{ name }}",
            "remval": "configure system id no name",
            "result": {
                "id": {
                    "name": "{{ name }}",
                },
            },
        },
        {
            "name": "id.location",
            "compval": "location",
            "getval": re.compile(
                r"^configure\ssystem\sid\slocation\s(?P<location>\S+)$"
            ),
            "setval": "configure system id location {{ location }}",
            "remval": "configure system id no location",
            "result": {
                "id": {
                    "location": "{{ location }}",
                },
            },
        },
        {
            "name": "id.contact",
            "compval": "contact",
            "getval": re.compile(
                r"^configure\ssystem\sid\scontact\s(?P<contact>\S+)$"
            ),
            "setval": "configure system id contact {{ contact }}",
            "remval": "configure system id no contact",
            "result": {
                "id": {
                    "contact": "{{ contact }}",
                },
            },
        },
        {
            "name": "security.ssh",
            "compval": "ssh",
            "getval": re.compile(
                r"^configure\ssystem\ssecurity\sssh\s((?P<negate>no\s)enable|enable)$"
            ),
            "setval": "configure system security ssh {% if ssh %}enable{% else %}no enable{% endif %}",
            "remval": "configure system security ssh no enable",
            "result": {
                "security": {
                    "ssh": "{{ False if negate is defined else True }}",
                },
            },
        },
        {
            "name": "security.telnet",
            "compval": "telnet",
            "getval": re.compile(
                r"^configure\ssystem\ssecurity\stelnet\s((?P<negate>no\s)enable|enable)$"
            ),
            "setval": "configure system security telnet {% if telnet %}enable{% else %}no enable{% endif %}",
            "remval": "configure system security telnet no enable",
            "result": {
                "security": {
                    "telnet": "{{ False if negate is defined else True }}",
                },
            },
        },
        {
            "name": "security.snmp",
            "compval": "snmp",
            "getval": re.compile(
                r"^configure\ssystem\ssecurity\ssnmp\s((?P<negate>no\s)enable|enable)$"
            ),
            "setval": "configure system security snmp {% if snmp %}enable{% else %}no enable{% endif %}",
            "remval": "configure system security snmp no enable",
            "result": {
                "security": {
                    "snmp": "{{ False if negate is defined else True }}",
                },
            },
        },
        {
            "name": "sntp.server",
            "compval": "server",
            "getval": re.compile(
                r"^configure\ssystem\ssntp\sserver\s(?P<server>\S+)$"
            ),
            "setval": "configure system sntp server {{ server }}",
            "remval": "configure system sntp no server",
            "result": {
                "sntp": {
                    "server": "{{ server }}",
                },
            },
        },
        {
            "name": "sntp.port",
            "compval": "port",
            "getval": re.compile(
                r"^configure\ssystem\ssntp\sport\s(?P<port>\d+)$"
            ),
            "setval": "configure system sntp port {{ port }}",
            "remval": "configure system sntp no port",
            "result": {
                "sntp": {
                    "port": "{{ port }}",
                },
            },
        },
        {
            "name": "sntp.poll_interval",
            "compval": "poll_interval",
            "getval": re.compile(
                r"^configure\ssystem\ssntp\spoll-interval\s(?P<poll_interval>\d+)$"
            ),
            "setval": "configure system sntp poll-interval {{ poll_interval }}",
            "remval": "configure system sntp no poll-interval",
            "result": {
                "sntp": {
                    "poll_interval": "{{ poll_interval }}",
                },
            },
        },
        {
            "name": "syslog.server",
            "compval": "server",
            "getval": re.compile(
                r"^configure\ssystem\ssyslog\sserver\s(?P<server>\S+)$"
            ),
            "setval": "configure system syslog server {{ server }}",
            "remval": "configure system syslog no server",
            "result": {
                "syslog": {
                    "server": "{{ server }}",
                },
            },
        },
        {
            "name": "syslog.facility",
            "compval": "facility",
            "getval": re.compile(
                r"^configure\ssystem\ssyslog\sfacility\s(?P<facility>\S+)$"
            ),
            "setval": "configure system syslog facility {{ facility }}",
            "remval": "configure system syslog no facility",
            "result": {
                "syslog": {
                    "facility": "{{ facility }}",
                },
            },
        },
        {
            "name": "syslog.severity",
            "compval": "severity",
            "getval": re.compile(
                r"^configure\ssystem\ssyslog\sseverity\s(?P<severity>\S+)$"
            ),
            "setval": "configure system syslog severity {{ severity }}",
            "remval": "configure system syslog no severity",
            "result": {
                "syslog": {
                    "severity": "{{ severity }}",
                },
            },
        },
        {
            "name": "sync_if_timing.mode",
            "compval": "mode",
            "getval": re.compile(
                r"^configure\ssystem\ssync-if-timing\smode\s(?P<mode>\S+)$"
            ),
            "setval": "configure system sync-if-timing mode {{ mode }}",
            "remval": "configure system sync-if-timing no mode",
            "result": {
                "sync_if_timing": {
                    "mode": "{{ mode }}",
                },
            },
        },
        {
            "name": "sync_if_timing.source",
            "compval": "source",
            "getval": re.compile(
                r"^configure\ssystem\ssync-if-timing\ssource\s(?P<source>\S+)$"
            ),
            "setval": "configure system sync-if-timing source {{ source }}",
            "remval": "configure system sync-if-timing no source",
            "result": {
                "sync_if_timing": {
                    "source": "{{ source }}",
                },
            },
        },
        {
            "name": "transaction.timeout",
            "compval": "timeout",
            "getval": re.compile(
                r"^configure\ssystem\stransaction\stimeout\s(?P<timeout>\d+)$"
            ),
            "setval": "configure system transaction timeout {{ timeout }}",
            "remval": "configure system transaction no timeout",
            "result": {
                "transaction": {
                    "timeout": "{{ timeout }}",
                },
            },
        },
    ]
    # fmt: on
