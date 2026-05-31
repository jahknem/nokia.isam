# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Xdsl_bondingTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Xdsl_bondingTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "group_assembly_time",
            "getval": re.compile(
                r"^configure\sxdsl-bonding\sgroup-assembly-time\s(?P<group_assembly_time>\d+)$"
            ),
            "setval": "configure xdsl-bonding group-assembly-time {{ group_assembly_time }}",
            "remval": "configure xdsl-bonding group-assembly-time",
            "result": {
                "group_assembly_time": "{{ group_assembly_time|int }}",
            },
        },
    ]
    # fmt: on
