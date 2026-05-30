# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


SEVERITY_CHOICES = ["indeterminate", "warning", "minor", "major", "critical"]
LOG_FULL_ACTION_CHOICES = ["wrap", "halt"]
FLTR_TYPE_CHOICES = ["temporal", "spatial"]
ALARM_ENTRY_CHOICES = [
    "all", "xtca-ne-es", "xtca-ne-ses", "xtca-ne-uas",
    "xtca-ne-day-es", "xtca-ne-day-ses", "xtca-ne-day-uas",
    "xtca-fe-es", "xtca-fe-ses", "xtca-fe-uas",
    "xtca-fe-day-es", "xtca-fe-day-ses", "xtca-fe-day-uas",
    "xtca-leftrs", "xtca-day-leftrs", "xtca-fe-leftrs", "xtca-fe-day-leftrs",
    "xtca-auto-port-reset", "xtca-reinit", "xtca-day-reinit",
    "xdsl-ne-los", "xdsl-ne-lof", "xdsl-ne-lom", "xdsl-ne-ese",
    "xdsl-act-cfg-error", "xdsl-act-not-feas", "xdsl-up-br-reach",
    "xdsl-ne-ncd", "xdsl-ne-lcd", "xdsl-fe-los", "xdsl-fe-lof",
    "xdsl-fe-lpr", "xdsl-fe-lol", "xdsl-fe-lom",
]


class AlarmArgs(object):
    """The arg spec for the isam_alarm module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "log": {
                    "type": "dict",
                    "options": {
                        "log_sev_level": {
                            "type": "str",
                            "choices": SEVERITY_CHOICES,
                        },
                        "log_full_action": {
                            "type": "str",
                            "choices": LOG_FULL_ACTION_CHOICES,
                        },
                        "non_itf_rep_sev_level": {
                            "type": "str",
                            "choices": SEVERITY_CHOICES,
                        },
                    },
                },
                "entries": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "index": {"type": "str", "required": True, "choices": ALARM_ENTRY_CHOICES},
                        "severity": {"type": "str", "choices": SEVERITY_CHOICES},
                        "service_affecting": {"type": "bool"},
                        "reporting": {"type": "bool"},
                        "logging": {"type": "bool"},
                    },
                },
                "filters": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "fltr_type": {"type": "str", "required": True, "choices": FLTR_TYPE_CHOICES},
                        "filterid": {"type": "int", "required": True},
                        "alarmid": {"type": "str", "choices": ALARM_ENTRY_CHOICES},
                        "status": {"type": "int"},
                        "threshold": {"type": "int"},
                        "window": {"type": "int"},
                        "suppressions": {
                            "type": "list",
                            "elements": "dict",
                            "options": {
                                "filterid": {"type": "int", "required": True},
                                "interface": {"type": "str"},
                                "alarmid": {"type": "str", "choices": ALARM_ENTRY_CHOICES},
                                "status": {"type": "int"},
                                "threshold": {"type": "int"},
                            },
                        },
                    },
                },
                "delta_log": {
                    "type": "dict",
                    "options": {
                        "indet_log_full_action": {"type": "str", "choices": LOG_FULL_ACTION_CHOICES},
                        "warn_log_full_action": {"type": "str", "choices": LOG_FULL_ACTION_CHOICES},
                        "minor_log_full_action": {"type": "str", "choices": LOG_FULL_ACTION_CHOICES},
                        "major_log_full_action": {"type": "str", "choices": LOG_FULL_ACTION_CHOICES},
                        "crit_log_full_act": {"type": "str", "choices": LOG_FULL_ACTION_CHOICES},
                    },
                },
                "custom_profiles": {
                    "type": "list",
                    "elements": "dict",
                    "options": dict({
                        "name": {"type": "str", "required": True},
                    }, **{
                        "mnemonic%d" % i: {"type": "str"}
                        for i in range(1, 6)
                    }, **{
                        "description%d" % i: {"type": "str"}
                        for i in range(1, 6)
                    }, **{
                        "visible%d" % i: {"type": "bool"}
                        for i in range(1, 6)
                    }, **{
                        "audible%d" % i: {"type": "bool"}
                        for i in range(1, 6)
                    }, **{
                        "polarity%d" % i: {"type": "str"}
                        for i in range(1, 6)
                    }, **{
                        "severity%d" % i: {"type": "str", "choices": SEVERITY_CHOICES}
                        for i in range(1, 6)
                    }),
                },
                "hgutr069_custs": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "alarm_id": {"type": "str", "required": True},
                        "description": {"type": "str"},
                    },
                },
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"],
            "default": "merged",
        },
    }
