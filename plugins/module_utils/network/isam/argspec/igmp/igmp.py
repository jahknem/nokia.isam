# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function


class IgmpArgs(object):
    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "mcast_svc_context": {"type": "str"},
                "mld_snooping": {"type": "bool"},
                "mld_querier": {"type": "bool"},
                "igmp_snooping": {"type": "bool"},
                "igmp_querier": {"type": "bool"},
                "query_interval": {"type": "int"},
                "query_response_interval": {"type": "int"},
                "robustness_count": {"type": "int"},
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"],
            "default": "merged",
        },
    }
