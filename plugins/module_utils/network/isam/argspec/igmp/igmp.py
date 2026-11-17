# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import copy

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.multicast.multicast import (
    IGMP_OPTIONS,
)


class IgmpArgs(object):
    argument_spec = {
        "config": {
            "type": "dict",
            "options": copy.deepcopy(IGMP_OPTIONS),
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"],
            "default": "merged",
        },
    }
