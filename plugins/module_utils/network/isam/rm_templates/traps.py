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

TRAP_TYPE_NAMES = [
    "cold-start-trap", "link-down-trap", "link-up-trap",
    "auth-fail-trap", "change-trap", "line-test-trap",
    "init-started-trap", "lic-key-chg-occr", "topology-chg",
    "selt-state-chg", "dhcp-sess-pre", "alarm-chg-trap",
    "phys-line-trap", "eqpt-change-trap", "success-set-trap",
    "other-alarm-trap", "warning-trap", "minor-trap", "major-trap",
    "critical-trap", "redundancy-trap", "eqpt-prot-trap",
    "craft-login-trap", "restart-trap", "ntr-trap", "rad-srvr-fail",
    "login-occr-trap", "logout-occr-trap", "trapmngr-chg-trap",
    "mst-genral", "mst-error", "mst-protocol-mig",
    "mst-inv-bpdu-rx", "mst-reg-conf-chg", "dying-gasp",
    "alrm-chg-occur", "mac-auth-fail", "new-ont-alrm",
    "ont-prov-status", "outofsync", "actual-cp-changed",
    "register-node", "avail-bw-changed", "login-occr6-trap",
    "logout-occr6-trap", "trapmgr-chg6-trap", "ont-prov-template",
    "auto-replan-board",
]

SHAPING_FIELDS = [
    ("max_per_window", "max-per-window"),
    ("window_size", "window-size"),
    ("max_queue_size", "max-queue-size"),
    ("min_interval", "min-interval"),
    ("min_severity", "min-severity"),
]

_BOOL_TRAP_NAMES = set(TRAP_TYPE_NAMES)
_SHAPING_NAME_SET = set(cli for _, cli in SHAPING_FIELDS)


def _split_multi_field(lines):
    result = []
    for line in lines:
        stripped = line.strip()
        if (stripped.startswith("configure trap manager ") or
                stripped.startswith("configure trap v6manager ")):
            tokens = stripped.split()
            if len(tokens) <= 5:
                result.append(stripped)
                continue
            prefix = " ".join(tokens[:4])
            result.append(prefix)
            i = 4
            while i < len(tokens):
                token = tokens[i]
                if token == "no":
                    if i + 1 < len(tokens):
                        result.append("%s no %s" % (prefix, tokens[i + 1]))
                        i += 2
                    else:
                        i += 1
                elif token in _BOOL_TRAP_NAMES or token == "priority":
                    if token == "priority" and i + 1 < len(tokens):
                        result.append("%s priority %s" % (prefix, tokens[i + 1]))
                        i += 2
                    elif token in _BOOL_TRAP_NAMES:
                        result.append("%s %s" % (prefix, token))
                        i += 1
                    else:
                        i += 1
                elif token in _SHAPING_NAME_SET:
                    if i + 1 < len(tokens):
                        result.append("%s %s %s" % (prefix, token, tokens[i + 1]))
                        i += 2
                    else:
                        i += 1
                else:
                    i += 1
        else:
            result.append(stripped)
    return result


class Isam_trapsTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        self.PARSERS = [
            {
                "name": "definition",
                "getval": re.compile(
                    r"^configure\strap\sdefinition\s(?P<name>\S+)$"
                ),
                "setval": "configure trap definition {{ name }}",
                "result": {
                    "definitions": {
                        "{{ name }}": {
                            "name": "{{ name }}",
                        }
                    }
                },
                "shared": True,
            },
            {
                "name": "definition.priority",
                "getval": re.compile(
                    r"^configure\strap\sdefinition\s(?P<name>\S+)\spriority\s(?P<priority>urgent|high|medium|low)$",
                ),
                "setval": "configure trap definition {{ name }} priority {{ priority }}",
                "result": {
                    "definitions": {
                        "{{ name }}": {
                            "name": "{{ name }}",
                            "priority": "{{ priority }}",
                        }
                    }
                },
            },
            {
                "name": "manager",
                "getval": re.compile(
                    r"^configure\strap\smanager\s(?P<address>\S+)$"
                ),
                "setval": "configure trap manager {{ address }}",
                "result": {
                    "managers": {
                        "{{ address }}": {
                            "address": "{{ address }}",
                        }
                    }
                },
                "shared": True,
            },
            {
                "name": "manager.priority",
                "getval": re.compile(
                    r"^configure\strap\smanager\s(?P<address>\S+)\spriority\s(?P<priority>urgent|high|medium|low)$",
                ),
                "setval": "configure trap manager {{ address }} priority {{ priority }}",
                "result": {
                    "managers": {
                        "{{ address }}": {
                            "address": "{{ address }}",
                            "priority": "{{ priority }}",
                        }
                    }
                },
            },
            {
                "name": "v6manager",
                "getval": re.compile(
                    r"^configure\strap\sv6manager\s(?P<ipv6address>\S+)$"
                ),
                "setval": "configure trap v6manager {{ ipv6address }}",
                "result": {
                    "v6managers": {
                        "{{ ipv6address }}": {
                            "ipv6address": "{{ ipv6address }}",
                        }
                    }
                },
                "shared": True,
            },
            {
                "name": "v6manager.priority",
                "getval": re.compile(
                    r"^configure\strap\sv6manager\s(?P<ipv6address>\S+)\spriority\s(?P<priority>urgent|high|medium|low)$",
                ),
                "setval": "configure trap v6manager {{ ipv6address }} priority {{ priority }}",
                "result": {
                    "v6managers": {
                        "{{ ipv6address }}": {
                            "ipv6address": "{{ ipv6address }}",
                            "priority": "{{ priority }}",
                        }
                    }
                },
            },
        ]
        for cli_name in TRAP_TYPE_NAMES:
            field = canonical_key(cli_name)
            for prefix, key_field, key_group in [
                ("manager", "address", "managers"),
                ("v6manager", "ipv6address", "v6managers"),
            ]:
                self.PARSERS.append({
                    "name": "%s.%s" % (prefix, field),
                    "getval": re.compile(
                        r"^configure\strap\s%s\s(?P<%s>\S+)\s((?P<negate>no\s)%s|%s)$" % (
                            prefix, key_field, cli_name, cli_name
                        ),
                    ),
                    "setval": "configure trap %s {{ %s }} {{ 'no ' if %s == false else '' }}%s" % (
                        prefix, key_field, field, cli_name
                    ),
                    "result": {
                        key_group: {
                            "{{ %s }}" % key_field: {
                                key_field: "{{ %s }}" % key_field,
                                field: "{{ False if negate is defined else True }}",
                            }
                        }
                    },
                })
        for field, cli_name in SHAPING_FIELDS:
            if field == "min_severity":
                getval_pat = (
                    r"^configure\strap\s%s\s(?P<%s>\S+)\s((?P<negate>no\s)%s|"
                    r"%s\s(?P<val>indeterminate|warning|minor|major|critical))$"
                )
            else:
                getval_pat = (
                    r"^configure\strap\s%s\s(?P<%s>\S+)\s((?P<negate>no\s)%s|"
                    r"%s\s(?P<val>\d+))$"
                )
            result_tpl = "{{ '' if negate is defined else val }}"
            if field == "min_severity":
                result_tpl = "{{ '' if negate is defined else val }}"
            for prefix, key_field, key_group in [
                ("manager", "address", "managers"),
                ("v6manager", "ipv6address", "v6managers"),
            ]:
                self.PARSERS.append({
                    "name": "%s.%s" % (prefix, field),
                    "getval": re.compile(
                        getval_pat % (prefix, key_field, cli_name, cli_name),
                    ),
                    "setval": (
                        "configure trap %s {{ %s }} "
                        "{{ 'no ' if negate else '%s ' + %s|string }}"
                    ) % (prefix, key_field, cli_name, field),
                    "result": {
                        key_group: {
                            "{{ %s }}" % key_field: {
                                key_field: "{{ %s }}" % key_field,
                                field: result_tpl,
                            }
                        }
                    },
                })
        if lines:
            lines = _split_multi_field(lines)
        super(Isam_trapsTemplate, self).__init__(lines=lines, tmplt=self, module=module)
