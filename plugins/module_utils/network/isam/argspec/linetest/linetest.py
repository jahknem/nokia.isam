# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function


SESSION_OPTIONS = {
    "session_id": {"type": "str", "required": True},
    "ownerid": {"type": "str"},
    "timeout_period": {"type": "str"},
    "line_num": {"type": "str"},
    "type_high": {"type": "str"},
    "type_low": {"type": "str"},
    "test_parm_num": {"type": "str"},
    "test_mode": {"type": "str", "choices": ["single", "interactive", "cablepair"]},
    "inactive_timer": {"type": "str"},
    "type_extend": {"type": "str"},
    "group_opt": {"type": "str", "choices": ["none", "extended", "pots-collective", "melt-collective"]},
    "busy_overwrite": {"type": "str", "choices": ["true", "false"]},
    "force_measure": {"type": "str", "choices": ["true", "false"]},
}

PARAMETER_OPTIONS = {
    "session_id": {"type": "str", "required": True},
    "test_name": {"type": "str", "required": True},
    "value1": {"type": "str"},
    "value2": {"type": "str"},
    "value3": {"type": "str"},
    "value4": {"type": "str"},
    "value5": {"type": "str"},
    "min_threshold": {"type": "str"},
    "max_threshold": {"type": "str"},
    "min_threshold2": {"type": "str"},
    "max_threshold2": {"type": "str"},
    "ltstrvalue1": {"type": "str"},
}


class LinetestArgs(object):
    """Argument specification for the safe LineTest resource."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "sessions": {"type": "list", "elements": "dict", "options": SESSION_OPTIONS},
                "parameters": {"type": "list", "elements": "dict", "options": PARAMETER_OPTIONS},
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"],
            "default": "merged",
        },
    }
