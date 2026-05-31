# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Equipment_replanTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Equipment_replanTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    PARSERS = [
        {
            "name": "board_auto_replan",
            "getval": re.compile(
                r"^configure\s+equipment\s+replan\s+boardautoreplan\s+(?P<board_auto_replan>\S+)\s*$"
            ),
            "setval": "configure equipment replan boardautoreplan {{ board_auto_replan }}",
            "remval": "configure equipment replan no boardautoreplan",
            "result": {
                "board_auto_replan": "{{ board_auto_replan }}",
            },
        },
    ]
