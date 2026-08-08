# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The InterfaceCages parser templates file. This contains
a list of parser definitions and associated functions that
facilitates both facts gathering and native command generation for
the given network resource.
"""

import re
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class InterfaceCagesTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(InterfaceCagesTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "cage.id",
            "getval": re.compile(
                r"""
                ^configure\sinterface\scage\s(?P<id>\S+)\s*$
                """, re.VERBOSE,
            ),
            "setval": "configure interface cage {{ id }}",
            "result": {
                "{{ id }}": {
                    "id": "{{ id }}",
                },
            },
            "shared": True,
        },
        {
            "name": "cage.operational_mode",
            "compval": "operational_mode",
            "getval": re.compile(
                r"^configure\sinterface\scage\s(?P<id>\S+)\soperational-mode\s(?P<operational_mode>\S+)\s*$"
            ),
            "setval": "configure interface cage {{ id }} operational-mode {{ operational_mode }}",
            "result": {
                "{{ id }}": {
                    "id": "{{ id }}",
                    "operational_mode": "{{ operational_mode }}",
                },
            },
        },
        {
            "name": "cage.description",
            "compval": "description",
            "getval": re.compile(
                r"""
                ^configure\sinterface\scage\s(?P<id>\S+)\s(?:(?P<negate>no\sdescription)|description\s(?P<description>.+))\s*$
                """, re.VERBOSE,
            ),
            "setval": "configure interface cage {{ id }} description {{ description }}",
            "remval": "configure interface cage {{ id }} no description",
            "result": {
                "{{ id }}": {
                    "id": "{{ id }}",
                    "description": "{{ description if description is defined else '' }}",
                },
            },
        },
        {
            "name": "cage.apply_qos",
            "compval": "apply_qos",
            "getval": re.compile(
                r"""
                ^configure\sinterface\scage\s(?P<id>\S+)\s(?P<negate>no\s)?(?P<apply_qos>apply-qos)\s*$
                """, re.VERBOSE,
            ),
            "setval": "configure interface cage {{ id }} {{ 'no apply-qos' if not apply_qos else 'apply-qos' }}",
            "remval": "configure interface cage {{ id }} no apply-qos",
            "result": {
                "{{ id }}": {
                    "id": "{{ id }}",
                    "apply_qos": "{{ False if negate is defined else True }}",
                },
            },
        },
    ]
    # fmt: on
