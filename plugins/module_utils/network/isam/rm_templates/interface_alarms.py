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
        {
            "name": "name",
            "getval": re.compile(
                r"^configure\s+interface\s+alarm\s+(?P<name>\S+)\s+.*$"
            ),
            "setval": "configure interface alarm {{ name }}",
            "result": {
                "{{ name }}": {
                    "name": "{{ name }}",
                }
            },
            "shared": True,
        },
        {
            "name": "default_severity",
            "getval": re.compile(
                r"^configure\s+interface\s+alarm\s+(?P<name>\S+)\s+default-severity\s+(?P<default_severity>\S+)\s*$"
            ),
            "setval": "configure interface alarm {{ name }} default-severity {{ default_severity }}",
            "remval": "configure interface alarm {{ name }} no default-severity",
            "result": {
                "{{ name }}": {
                    "name": "{{ name }}",
                    "default_severity": "{{ default_severity }}",
                }
            },
        },
    ]
