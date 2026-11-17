# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


SEVERITY_CHOICES = ["indeterminate", "warning", "minor", "major", "critical"]
LOG_FULL_ACTION_CHOICES = ["wrap", "halt"]
FLTR_TYPE_CHOICES = ["temporal", "spatial"]
ENTRY_SEVERITY_CHOICES = SEVERITY_CHOICES + ["ignore"]
FLTR_STATUS_CHOICES = ["not-used", "used"]
SUPPRESSION_ALARM_CHOICES = ["board-missing", "board-init"]
# Entry indexes and filter alarmids are alarm types (<Alarm::alarmIndexExt>): the
# R6.2.04 CLI help lists 1243 of them (door, board-missing, ONT/MDU/SFU types, ...)
# and the set changes with the release, so they are not restricted here; the
# device validates them.


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
                        "index": {"type": "str", "required": True},
                        "severity": {"type": "str", "choices": ENTRY_SEVERITY_CHOICES},
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
                        "alarmid": {"type": "str"},
                        "status": {"type": "str", "choices": FLTR_STATUS_CHOICES},
                        "threshold": {"type": "int"},
                        "window": {"type": "int"},
                        "suppressions": {
                            "type": "list",
                            "elements": "dict",
                            "options": {
                                "filterid": {"type": "int", "required": True},
                                "interface": {"type": "str"},
                                "alarmid": {"type": "str", "choices": SUPPRESSION_ALARM_CHOICES},
                                "status": {"type": "str", "choices": FLTR_STATUS_CHOICES},
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
