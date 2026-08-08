# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function


class Mcast_controlArgs(object):
    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "mcast_svc_context": {"type": "str"},
                "admin_state": {"type": "bool"},
                "max_groups": {"type": "int"},
                "max_sources": {"type": "int"},
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"],
            "default": "merged",
        },
    }
