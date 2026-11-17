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


# ---------------------------------------------------------------------------
# configure system sync-if-timing (structure from real 'info configure detail flat')
#
#   configure system sync-if-timing [no] revert [no] wait-time <n> output-ql-thresh <ql>
#       [no] ssmout-en-bits ssmout-ceiling <ql> [no] ais-sensitivity
#   configure system sync-if-timing bits <mode>
#   configure system sync-if-timing bits-bind [no] bits-a-bind <x> [no] bits-b-bind <x>
#   configure system sync-if-timing force-reference <ref>|none
#   configure system sync-if-timing ref-order prio1|prio2 <ref>|none
#   configure system sync-if-timing ssm <reference> [no] ssmenable default-ql <ql> target-ql <ql>
#   configure system sync-if-timing synce <reference> <port>|none
#   configure system sync-if-timing ssmout-synce <port> [no] ssmout-enable
#
# Resets: force-reference, ref-order and synce go back to 'none' (the device's own
# unset value); every other attribute is reset with 'no <attr>'.
# ---------------------------------------------------------------------------

SYNC_PREFIX = "configure system sync-if-timing"
SYNC_TOP_FIELDS = {
    "revert": "bool",
    "wait_time": "int",
    "output_ql_thresh": "str",
    "ssmout_en_bits": "bool",
    "ssmout_ceiling": "str",
    "ais_sensitivity": "bool",
}
SYNC_BITS_BIND_FIELDS = {"bits_a_bind": "str", "bits_b_bind": "str"}
SYNC_SSM_FIELDS = {"ssmenable": "bool", "default_ql": "str", "target_ql": "str"}
SYNC_SSMOUT_FIELDS = {"ssmout_enable": "bool"}
SYNC_REF_ORDER = ("prio1", "prio2")
# list -> (CLI node, identity field)
SYNC_LISTS = {
    "ssm": ("ssm", "reference"),
    "synce": ("synce", "reference"),
    "ssmout_synce": ("ssmout-synce", "port"),
}
# fields of sync_if_timing handled by the template PARSERS (compare framework)
SYNC_LEGACY_FIELDS = ("mode", "source")


def _sync_kebab(key):
    return key.replace("_", "-")


def _sync_quote(value):
    value = str(value)
    return '"' + value + '"' if value == "" or re.search(r"\s", value) else value


def _sync_attrs(tokens, fields, target):
    """Parse '[no] <attr> [value]' tokens into target; False when a token is unknown."""
    cli = dict((_sync_kebab(k), k) for k in fields)
    i = 0
    known = True
    while i < len(tokens):
        negate = tokens[i] == "no" and i + 1 < len(tokens)
        key = tokens[i + 1] if negate else tokens[i]
        if key not in cli:
            known = False
            i += 2 if negate else 1
            continue
        field = cli[key]
        ftype = fields[field]
        if ftype == "bool":
            target[field] = not negate
            i += 2 if negate else 1
        elif negate:
            target.pop(field, None)
            i += 2
        elif i + 1 < len(tokens):
            value = tokens[i + 1].strip('"')
            target[field] = int(value) if ftype == "int" and value.lstrip("-").isdigit() else value
            i += 2
        else:
            known = False
            i += 1
    return known


def parse_sync_if_timing(values, sync):
    """Parse the tokens after 'configure system sync-if-timing' into the sync dict.

    Returns True when the line is understood (mode/source are left to PARSERS).
    """
    if not values:
        return False
    head = values[0]
    if head in SYNC_LEGACY_FIELDS:
        return True
    if head in ("bits", "force-reference") and len(values) == 2:
        sync[head.replace("-", "_")] = values[1]
        return True
    if head == "bits-bind":
        return _sync_attrs(values[1:], SYNC_BITS_BIND_FIELDS, sync.setdefault("bits_bind", {}))
    if head == "ref-order" and len(values) == 3 and values[1] in SYNC_REF_ORDER:
        sync.setdefault("ref_order", {})[values[1]] = values[2]
        return True
    if head == "ssm" and len(values) >= 2:
        entry = {"reference": values[1]}
        sync.setdefault("ssm", []).append(entry)
        return _sync_attrs(values[2:], SYNC_SSM_FIELDS, entry)
    if head == "synce" and len(values) == 3:
        sync.setdefault("synce", []).append({"reference": values[1], "port": values[2]})
        return True
    if head == "ssmout-synce" and len(values) >= 2:
        entry = {"port": values[1]}
        sync.setdefault("ssmout_synce", []).append(entry)
        return _sync_attrs(values[2:], SYNC_SSMOUT_FIELDS, entry)
    return _sync_attrs(values, SYNC_TOP_FIELDS, sync)


def _sync_parts(fields, values, reset=False):
    parts = []
    for field, value in values.items():
        if field not in fields or value is None:
            continue
        cli = _sync_kebab(field)
        if reset or (fields[field] == "bool" and not value):
            parts.append("no " + cli)
        elif fields[field] == "bool":
            parts.append(cli)
        else:
            parts.append("{0} {1}".format(cli, _sync_quote(value)))
    return parts


def render_sync_if_timing(values, reset=False):
    """Commands setting (or with reset=True resetting) the given sync-if-timing values.

    values has the shape of the sync_if_timing option (lists contain only the
    instances and attributes to render, each with its identity).
    """
    commands = []
    parts = _sync_parts(SYNC_TOP_FIELDS, values, reset)
    if parts:
        commands.append(SYNC_PREFIX + " " + " ".join(parts))
    if values.get("bits") is not None:
        commands.append(SYNC_PREFIX + (" no bits" if reset else " bits " + values["bits"]))
    parts = _sync_parts(SYNC_BITS_BIND_FIELDS, values.get("bits_bind") or {}, reset)
    if parts:
        commands.append(SYNC_PREFIX + " bits-bind " + " ".join(parts))
    if values.get("force_reference") is not None:
        commands.append(SYNC_PREFIX + " force-reference " + ("none" if reset else values["force_reference"]))
    for prio in SYNC_REF_ORDER:
        value = (values.get("ref_order") or {}).get(prio)
        if value is not None:
            commands.append("{0} ref-order {1} {2}".format(SYNC_PREFIX, prio, "none" if reset else value))
    for entry in values.get("ssm") or []:
        parts = _sync_parts(SYNC_SSM_FIELDS, entry, reset)
        if parts:
            commands.append("{0} ssm {1} {2}".format(SYNC_PREFIX, entry["reference"], " ".join(parts)))
    for entry in values.get("synce") or []:
        if entry.get("port") is not None:
            commands.append("{0} synce {1} {2}".format(SYNC_PREFIX, entry["reference"], "none" if reset else entry["port"]))
    for entry in values.get("ssmout_synce") or []:
        parts = _sync_parts(SYNC_SSMOUT_FIELDS, entry, reset)
        if parts:
            commands.append("{0} ssmout-synce {1} {2}".format(SYNC_PREFIX, entry["port"], " ".join(parts)))
    return commands
