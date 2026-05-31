# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class MulticastArgs(object):
    """The arg spec for the isam_multicast module."""

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "igmp": {
                    "type": "dict",
                    "options": {
                        "mld_snooping": {"type": "bool"},
                        "mld_querier": {"type": "bool"},
                        "igmp_snooping": {"type": "bool"},
                        "igmp_querier": {"type": "bool"},
                        "query_interval": {"type": "int"},
                        "query_response_interval": {"type": "int"},
                        "robustness_count": {"type": "int"},
                    },
                },
                "mcast_control": {
                    "type": "dict",
                    "options": {
                        "admin_state": {"type": "bool"},
                        "max_groups": {"type": "int"},
                        "max_sources": {"type": "int"},
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
