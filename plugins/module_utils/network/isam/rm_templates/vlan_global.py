# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Isam_vlan_globalTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Isam_vlan_globalTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            # configure vlan broadcast-frames [ no priority-policy | priority-policy <value> ]
            # (real 'info configure detail flat': 'priority-policy vlan-specific'; the
            # 'no priority-policy' reset form is unverified on a device)
            "name": "broadcast_frames.priority_policy",
            "compval": "priority_policy",
            "getval": re.compile(
                r"^configure\s+vlan\s+broadcast-frames\s+"
                r"(?:no\s+priority-policy|priority-policy\s+(?P<priority_policy>\S+))(?:\s.*)?$"
            ),
            "setval": "configure vlan broadcast-frames priority-policy {{ priority_policy }}",
            "remval": "configure vlan broadcast-frames no priority-policy",
            "result": {
                "broadcast_frames": {
                    "priority_policy": "{{ priority_policy }}",
                },
            },
        },
        {
            "name": "broadcast_frames.drop_unknown_multicast",
            "compval": "drop_unknown_multicast",
            "getval": re.compile(
                r"^configure\s+vlan\s+broadcast-frames\s+((?P<negate>no\s+)?drop-unknown-multicast)$"
            ),
            "setval": "configure vlan broadcast-frames drop-unknown-multicast",
            "remval": "configure vlan broadcast-frames no drop-unknown-multicast",
            "result": {
                "broadcast_frames": {
                    "drop_unknown_multicast": "{{ False if negate is defined else True }}",
                },
            },
        },
        {
            "name": "priority_regen",
            "getval": re.compile(
                r"""
                ^configure\svlan\spriority-regen\s(?P<id>\d+)
                (?:\sprofile-name\s(?P<profile_name>\S+))?
                (?:\spbit0\s(?P<pbit0>\d+))?
                (?:\spbit1\s(?P<pbit1>\d+))?
                (?:\spbit2\s(?P<pbit2>\d+))?
                (?:\spbit3\s(?P<pbit3>\d+))?
                (?:\spbit4\s(?P<pbit4>\d+))?
                (?:\spbit5\s(?P<pbit5>\d+))?
                (?:\spbit6\s(?P<pbit6>\d+))?
                (?:\spbit7\s(?P<pbit7>\d+))?
                \s*$""",
                re.VERBOSE,
            ),
            "setval": "configure vlan priority-regen {{ priority_regen.id }}"
                      "{% if priority_regen.profile_name is defined and priority_regen.profile_name is not none %} profile-name {{ priority_regen.profile_name }}{% endif %}"
                      "{% for bit in range(8) %}{% set key = 'pbit' ~ bit %}"
                      "{% if priority_regen[key] is defined and priority_regen[key] is not none %} {{ key }} {{ priority_regen[key] }}{% endif %}"
                      "{% endfor %}",
            "remval": "configure vlan no priority-regen {{ priority_regen.id }}",
            "result": {
                "priority_regen": {
                    "{{ id }}": {
                        "id": "{{ id }}",
                        "profile_name": "{{ profile_name }}",
                        "pbit0": "{{ pbit0 }}",
                        "pbit1": "{{ pbit1 }}",
                        "pbit2": "{{ pbit2 }}",
                        "pbit3": "{{ pbit3 }}",
                        "pbit4": "{{ pbit4 }}",
                        "pbit5": "{{ pbit5 }}",
                        "pbit6": "{{ pbit6 }}",
                        "pbit7": "{{ pbit7 }}",
                    },
                },
            },
        },
        {
            "name": "tpid.value",
            "compval": "value",
            "getval": re.compile(
                r"^configure\s+vlan\s+tpid\s+(?:(?P<index>\d+)\s+value\s+)?(?P<value>\S+)$"
            ),
            "setval": "configure vlan tpid {{ value }}",
            "remval": "configure vlan no tpid",
            "result": {
                "tpid": {
                    "value": "{{ value }}",
                },
            },
        },
        {
            "name": "tpid.no_value",
            "compval": "value",
            "getval": re.compile(r"^configure\s+vlan\s+no\s+tpid$"),
            "setval": "configure vlan tpid {{ value }}",
            "remval": "configure vlan no tpid",
            "result": {"tpid": {}},
        },
        {
            "name": "vmac_address_format.format",
            "compval": "format",
            "getval": re.compile(
                r"^configure\s+vlan\s+vmac-address-format\s+(?P<format>\S+)(?:\s+(?P<host_id>\d+))?$"
            ),
            "setval": "configure vlan vmac-address-format {{ format }}{% if host_id is defined %} {{ host_id }}{% endif %}",
            "remval": "configure vlan no vmac-address-format",
            "result": {
                "vmac_address_format": {
                    "format": "{{ format }}",
                    "host_id": "{{ host_id }}",
                },
            },
        },
        {
            "name": "vmac_address_format.no_format",
            "compval": "format",
            "getval": re.compile(r"^configure\s+vlan\s+no\s+vmac-address-format$"),
            "setval": "configure vlan vmac-address-format {{ format }}",
            "remval": "configure vlan no vmac-address-format",
            "result": {"vmac_address_format": {}},
        },
    ]
    # fmt: on
