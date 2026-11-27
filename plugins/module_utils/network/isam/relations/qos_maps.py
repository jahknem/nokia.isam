# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the qos_maps family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "sections": {
        "dn_ctrl_pkt": {"identity": "protocol", "scope": "device_global"},
        "dscp_map_dot1p": {"identity": "dscp", "scope": "device_global"},
        "tc_map_dot1p": {"identity": "dot1p", "scope": "device_global"},
        "up_ctrl_pkt": {"identity": "protocol", "scope": "device_global"},
    },
}
