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
                r"^configure\s+vlan\s+priority-regen\s+dot1p\s+(?P<dot1p>\d+)\s+regen-dot1p\s+(?P<regen_dot1p>\d+)$"
            ),
            "setval": "configure vlan priority-regen dot1p {{ priority_regen.dot1p }} regen-dot1p {{ priority_regen.regen_dot1p }}",
            "remval": "configure vlan priority-regen dot1p {{ priority_regen.dot1p }} no regen-dot1p",
            "result": {
                "priority_regen": {
                    "{{ dot1p }}": {
                        "dot1p": "{{ dot1p }}",
                        "regen_dot1p": "{{ regen_dot1p }}",
                    },
                },
            },
        },
        {
            "name": "tpid.value",
            "compval": "value",
            "getval": re.compile(
                r"^configure\s+vlan\s+tpid\s+(?P<value>\S+)$"
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
                r"^configure\s+vlan\s+vmac-address-format\s+(?P<format>\S+)$"
            ),
            "setval": "configure vlan vmac-address-format {{ format }}",
            "remval": "configure vlan no vmac-address-format",
            "result": {
                "vmac_address_format": {
                    "format": "{{ format }}",
                },
            },
        },
    ]
    # fmt: on
