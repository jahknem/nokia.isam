# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Link_aggArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_link_agg module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "ports": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "id": {"type": "str", "required": True, "aliases": ["name"]},
                        "lacp_mode": {
                            "type": "str",
                            "choices": ["active", "passive"],
                            "aliases": ["mode"],
                        },
                        "passive_lacp": {"type": "bool"},
                        "timeout": {"type": "str", "choices": ["long", "short"]},
                        "short_timeout": {"type": "bool"},
                        "actor_port_prio": {"type": "str"},
                    },
                },
                "groups": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "id": {"type": "str", "required": True, "aliases": ["name"]},
                        "load_sharing_policy": {
                            "type": "str",
                            "choices": [
                                "mac-src",
                                "mac-dst",
                                "mac-src-dst",
                                "ip-src",
                                "ip-dst",
                                "ip-src-dst",
                                "l2-l3-hybrid-model",
                            ],
                        },
                        "max_active_port": {"type": "str"},
                        "swo_threshold": {"type": "str"},
                        "priority": {"type": "str"},
                        "swo_revert": {"type": "str", "choices": ["disable", "enable"]},
                        "mode": {"type": "str", "choices": ["static", "dynamic"]},
                        "master_iwf": {"type": "str", "choices": ["auto", "unset"]},
                        "ports": {"type": "list", "elements": "str"},
                    },
                },
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": [
                "merged",
                "replaced",
                "overridden",
                "deleted",
                "gathered",
                "rendered",
                "parsed",
            ],
            "default": "merged",
        },
    }
