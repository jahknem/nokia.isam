# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.voice_sip.voice_sip import (
    Isam_voice_sipFacts,
)


class Isam_voice_sipTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Isam_voice_sipTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    def parse(self):
        """Parse packed detail-flat lines with the shared Voice SIP parser."""
        lines = self._lines or []
        return Isam_voice_sipFacts._parse_voice_sip(
            [line.strip() for line in lines if line.strip()]
        )

    # fmt: off
    PARSERS = [
        {
            "name": "lineid_syn_prof",
            "getval": re.compile(
                r"^configure voice sip lineid-syn-prof\s+(?P<name>\S+)(?:\s+.*)?$"
            ),
            "setval": "configure voice sip lineid-syn-prof {{ name }}",
            "remval": "configure voice sip no lineid-syn-prof {{ name }}",
            "shared": True,
            "result": {
                "lineid_syn_prof": {
                    "{{ name }}": {},
                },
            },
        },
        {
            "name": "vsp.id",
            "getval": re.compile(
                r"^configure voice sip vsp\s+(?P<name>\S+)(?:\s+.*)?$"
            ),
            "setval": "configure voice sip vsp {{ name }}",
            "remval": "configure voice sip no vsp {{ name }}",
            "shared": True,
            "result": {
                "vsp": {
                    "{{ name }}": {},
                },
            },
        },
        {
            "name": "register.id",
            "getval": re.compile(
                r"^configure voice sip register\s+(?P<name>\S+)(?:\s+.*)?$"
            ),
            "setval": "configure voice sip register {{ name }}",
            "remval": "configure voice sip no register {{ name }}",
            "shared": True,
            "result": {
                "register": {
                    "{{ name }}": {},
                },
            },
        },
        {
            "name": "redundancy.id",
            "getval": re.compile(
                r"^configure voice sip redundancy\s+(?P<name>\S+)(?:\s+.*)?$"
            ),
            "setval": "configure voice sip redundancy {{ name }}",
            "remval": "configure voice sip no redundancy {{ name }}",
            "shared": True,
            "result": {
                "redundancy": {
                    "{{ name }}": {},
                },
            },
        },
        {
            "name": "system.id",
            "getval": re.compile(
                r"^configure voice sip system(?:\s+.*)?$"
            ),
            "setval": "configure voice sip system",
            "result": {
                "system": {},
            },
        },
        {
            "name": "redundancy_cmd.id",
            "getval": re.compile(
                r"^configure voice sip redundancy-cmd\s+(?P<name>\S+)(?:\s+.*)?$"
            ),
            "setval": "configure voice sip redundancy-cmd {{ name }}",
            "remval": "configure voice sip no redundancy-cmd {{ name }}",
            "shared": True,
            "result": {
                "redundancy_cmd": {
                    "{{ name }}": {},
                },
            },
        },
        {
            "name": "statistics.id",
            "getval": re.compile(
                r"^configure voice sip statistics(?:\s+.*)?$"
            ),
            "setval": "configure voice sip statistics",
            "result": {
                "statistics": {},
            },
        },
        {
            "name": "cas_nsm_prof.id",
            "getval": re.compile(
                r"^configure voice sip cas-nsm-prof\s+(?P<name>\S+)(?:\s+.*)?$"
            ),
            "setval": "configure voice sip cas-nsm-prof {{ name }}",
            "remval": "configure voice sip no cas-nsm-prof {{ name }}",
            "shared": True,
            "result": {
                "cas_nsm_prof": {
                    "{{ name }}": {},
                },
            },
        },
    ]
    # fmt: on
