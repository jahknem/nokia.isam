# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the link_agg family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "sections": {
        # 'configure link-agg group' has no create/delete form (device help): the device keeps
        # one group per Ethernet port, at the port's index, with the port as its default member
        # ('link-agg group <g> no port <g>' refused with error 22, live 2026-11-18).
        "groups": {
            "identity": "id", "object": "lag",
            "created_with": [{"prefix": None, "object": "lag", "default": None}],
        },
        "ports": {"identity": "id", "object": "ethernet_port"},
    },
}
