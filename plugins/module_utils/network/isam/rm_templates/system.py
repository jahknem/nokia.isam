# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    canonical_key,
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
            "name": "security.welcome_banner",
            "compval": "welcome_banner",
            "getval": re.compile(
                r"^configure\ssystem\ssecurity\swelcome-banner\s"
                r"(?:\"(?P<quoted_banner>[^\"]*)\"|(?P<welcome_banner>\S+))$"
            ),
            "setval": "configure system security welcome-banner \"{{ welcome_banner }}\"",
            "remval": "configure system security no welcome-banner",
            "result": {
                "security": {
                    "welcome_banner": "{{ quoted_banner if quoted_banner is defined else welcome_banner }}",
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
        {
            "name": "max_lt_link_speed",
            "compval": "max_lt_link_speed",
            "getval": re.compile(
                r"^configure\ssystem\smax-lt-link-speed\slink-speed\s(?P<max_lt_link_speed>\S+)$"
            ),
            "setval": "configure system max-lt-link-speed link-speed {{ max_lt_link_speed }}",
            "remval": "configure system max-lt-link-speed no link-speed",
            "result": {
                "max_lt_link_speed": "{{ max_lt_link_speed }}",
            },
        },
    ]
    # fmt: on


def _syntax_parser(section, field, cli_name):
    section_key = canonical_key(section)
    return {
        "name": section_key + "." + field,
        "compval": field,
        "getval": re.compile(
            r"^configure\ssystem\s" + re.escape(section) + r"\s"
            + re.escape(cli_name)
            + r"\s(?:\"(?P<quoted>[^\"]*)\"|(?P<value>\S+))$"
        ),
        "setval": "configure system " + section + " " + cli_name + ' "{{ ' + field + ' }}"',
        "remval": "configure system " + section + " no " + cli_name,
        "result": {
            section_key: {
                field: "{{ quoted if quoted is defined else value }}",
            },
        },
    }


Isam_systemTemplate.PARSERS.extend(
    [
        _syntax_parser("loop-id-syntax", "atm_based_dsl", "atm-based-dsl"),
        _syntax_parser("loop-id-syntax", "efm_based_dsl", "efm-based-dsl"),
        _syntax_parser("loop-id-syntax", "efm_based_pon", "efm-based-pon"),
        _syntax_parser("loop-id-syntax", "efm_based_epon", "efm-based-epon"),
        _syntax_parser("loop-id-syntax", "efm_based_ngpon2", "efm-based-ngpon2"),
        _syntax_parser("relay-id-syntax", "atm_based_dsl", "atm-based-dsl"),
        _syntax_parser("relay-id-syntax", "efm_based_dsl", "efm-based-dsl"),
    ]
)


def _sntp_parser(field, cli_name, value_pattern=r"\S+", value_filter=""):
    value = "{{ '' if negate is defined else value" + value_filter + " }}"
    return {
        "name": "sntp." + field,
        "compval": field,
        "getval": re.compile(
            r"^configure\ssystem\ssntp\s"
            + re.escape(cli_name)
            + r"\s(?:(?P<negate>no\s+)|(?P<value>" + value_pattern + r"))$"
        ),
        "setval": "configure system sntp {{ 'no " + cli_name + "' if " + field + " is none else '" + cli_name + " ' + " + field + "|string }}",
        "remval": "configure system sntp no " + cli_name,
        "result": {"sntp": {field: value}},
    }


Isam_systemTemplate.PARSERS.extend(
    [
        {
            "name": "sntp.enabled",
            "compval": "enabled",
            "getval": re.compile(r"^configure\ssystem\ssntp\s(?P<negate>no\s+)?enable$"),
            "setval": "configure system sntp {{ 'no enable' if not enabled else 'enable' }}",
            "remval": "configure system sntp no enable",
            "result": {"sntp": {"enabled": "{{ False if negate is defined else True }}"}},
        },
        _sntp_parser("server_ip_addr", "server-ip-addr"),
        _sntp_parser("polling_rate", "polling-rate", r"\d+", "|int"),
        _sntp_parser("timezone_offset", "timezone-offset", r"-?\d+", "|int"),
    ]
)
