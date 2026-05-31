# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class IphostTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(IphostTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "name",
            "getval": re.compile(
                r"""
                ^configure\siphost\sname\s(?P<name>.+?)
                $""", re.VERBOSE),
            "setval": "configure iphost name {{ name }}",
            "result": {
                "name": "{{ name }}",
            },
        },
    ]
    # fmt: on
