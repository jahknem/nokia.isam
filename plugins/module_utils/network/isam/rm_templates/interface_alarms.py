# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Interface_alarmsTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Interface_alarmsTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    PARSERS = [
        # default_severity must come first: NetworkTemplate.parse() stops at the first matching
        # parser, so the catch-all "name" parser would otherwise swallow default-severity lines.
        {
            "name": "default_severity",
            "getval": re.compile(
                r"^configure\s+interface\s+alarm\s+(?P<name>\S+)\s+(?:(?P<negate>no\s+)default-severity|default-severity\s+(?P<default_severity>\S+))\s*$"
            ),
            "setval": "configure interface alarm {{ name }} default-severity {{ default_severity }}",
            "remval": "configure interface alarm {{ name }} no default-severity",
            "result": {
                "{{ name }}": {
                    "name": "{{ name }}",
                    "default_severity": "{{ '' if negate is defined else default_severity }}",
                }
            },
        },
        {
            "name": "name",
            "getval": re.compile(
                r"^configure\s+interface\s+alarm\s+(?P<name>\S+)(?:\s+.*)?$"
            ),
            "setval": "configure interface alarm {{ name }}",
            "result": {
                "{{ name }}": {
                    "name": "{{ name }}",
                }
            },
        },
    ]
