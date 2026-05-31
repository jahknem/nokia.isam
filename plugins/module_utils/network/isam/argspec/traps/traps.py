# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

PRIORITY_CHOICES = ["urgent", "high", "medium", "low"]
SEVERITY_CHOICES = ["indeterminate", "warning", "minor", "major", "critical"]

TRAP_NAME_CHOICES = [
    "cold-start", "link-down", "link-up", "auth-failure",
    "change-occured", "line-test-report", "init-started",
    "lic-key-chg-occr", "topology-chg", "selt-state-chg",
    "dhcp-sess-pre", "radius-server-failure", "login-occured",
    "logout-occured", "trapmngr-chg-occr", "mst-genral",
    "mst-error", "mst-protocol-mig", "mst-inv-bpdu-rx",
    "mst-reg-conf-chg", "alrm-change-occured", "out-of-sync",
    "actual-cp-changed", "avail-bw-changed", "mac-auth-failure",
    "new-ont-alrm", "ont-prov-status", "sw-upgrade-finished",
    "login-occuredv6", "logout-occuredv6", "trapmngr-chg-occrv6",
    "ont-prov-template", "auto-replan-board",
]

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


def _trap_field(name):
    return name.replace("-", "_")


TRAP_TYPE_OPTS = {_trap_field(n): {"type": "bool"} for n in TRAP_TYPE_NAMES}

SHAPING_OPTS = {
    "max_per_window": {"type": "int"},
    "window_size": {"type": "int"},
    "max_queue_size": {"type": "int"},
    "min_interval": {"type": "int"},
    "min_severity": {"type": "str", "choices": SEVERITY_CHOICES},
}

MANAGER_OPTS = {
    "address": {"type": "str", "required": True},
    "priority": {"type": "str", "choices": PRIORITY_CHOICES},
}
MANAGER_OPTS.update(TRAP_TYPE_OPTS)
MANAGER_OPTS.update(SHAPING_OPTS)

V6MANAGER_OPTS = {
    "ipv6address": {"type": "str", "required": True},
    "priority": {"type": "str", "choices": PRIORITY_CHOICES},
}
V6MANAGER_OPTS.update(TRAP_TYPE_OPTS)
V6MANAGER_OPTS.update(SHAPING_OPTS)

DEFINITION_OPTS = {
    "name": {"type": "str", "required": True, "choices": TRAP_NAME_CHOICES},
    "priority": {"type": "str", "choices": PRIORITY_CHOICES},
}


class Isam_trapsArgs(object):
    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "definitions": {
                    "type": "list",
                    "elements": "dict",
                    "options": dict(DEFINITION_OPTS),
                },
                "managers": {
                    "type": "list",
                    "elements": "dict",
                    "options": dict(MANAGER_OPTS),
                },
                "v6managers": {
                    "type": "list",
                    "elements": "dict",
                    "options": dict(V6MANAGER_OPTS),
                },
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": [
                "merged", "replaced", "overridden", "deleted",
                "gathered", "rendered", "parsed",
            ],
            "default": "merged",
        },
    }
