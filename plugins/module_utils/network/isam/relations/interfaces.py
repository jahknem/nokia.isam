# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the interfaces family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "targeted_writes": True,
    "sections": {
        "config": {
            "identity": "name",
            "object": "interface",
            # Live-verified on DS-LIN-TEST-01 (R6.2): the device creates these entries itself, at
            # exactly these defaults, with the ONT and with a VLAN joining a bridge port. A
            # differing entry was customized. Live read 2026-11-25: 359 of 359 port VLANs have
            # their vlan-port: entry and no vlan-port: entry exists without one.
            "created_with": [
                {"prefix": "ont:", "object": "ont", "default": {"admin_up": True, "link_updown_trap": True}},
                {
                    "prefix": "vlan-port:", "object": "vlan_port",
                    "default": {"admin_up": True, "link_updown_trap": False, "severity": "no-value"},
                },
            ],
        },
    },
}
