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
            "name": "priority_regen.dot1p",
            "compval": "priority_regen",
            "getval": re.compile(
                r"^configure\s+vlan\s+priority-regen\s+dot1p\s+(?P<dot1p>\d+)\s+regen-dot1p\s+(?P<regen_dot1p>\d+)$|^configure\s+vlan\s+priority-regen\s+(?P<profile_id>\d+)\s+profile-name\s+(?P<profile_name>\S+)\s+pbit0\s+(?P<pbit0>\d+)\s+pbit1\s+(?P<pbit1>\d+)\s+pbit2\s+(?P<pbit2>\d+)\s+pbit3\s+(?P<pbit3>\d+)\s+pbit4\s+(?P<pbit4>\d+)\s+pbit5\s+(?P<pbit5>\d+)\s+pbit6\s+(?P<pbit6>\d+)\s+pbit7\s+(?P<pbit7>\d+)$"
            ),
            "setval": "configure vlan priority-regen dot1p {{ priority_regen.dot1p }} regen-dot1p {{ priority_regen.regen_dot1p }}",
            "remval": "configure vlan priority-regen dot1p {{ priority_regen.dot1p }} no regen-dot1p",
            "result": {
                "priority_regen": {
                    "{{ dot1p|default(profile_id) }}": {
                        "dot1p": "{{ dot1p|default(profile_id) }}",
                        "regen_dot1p": "{{ regen_dot1p }}",
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
    ]
    # fmt: on
