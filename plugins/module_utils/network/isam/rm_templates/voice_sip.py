# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Isam_voice_sipTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Isam_voice_sipTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "lineid_syn_prof",
            "getval": re.compile(
                r"^configure voice sip lineid-syn-prof\s+(?P<name>\S+)(?:\s+.*)?$"
            ),
            "setval": "configure voice sip lineid-syn-prof {{ name }}",
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
            "shared": True,
            "result": {
                "cas_nsm_prof": {
                    "{{ name }}": {},
                },
            },
        },
    ]
    # fmt: on
