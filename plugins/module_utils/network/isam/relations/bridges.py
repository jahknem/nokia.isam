# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the bridges family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "targeted_writes": True,
    "settings": ("ageing_time",),
    "sections": {
        # 'configure bridge ( no port (port) ) | ( port (port) ... )' creates the bridge port.
        "port": {
            "identity": "port", "object": "bridge_port", "creates": True,
            "requires": [
                # A port joins only an existing VLAN: the forwarding VLAN (l2fwder_vlan) when the
                # entry names one, otherwise the VLAN id itself.
                {"section": "vlans.config",
                 "evidence": "live read DS-LIN-TEST-01 2026-11-25: all 359 port VLANs resolve to a VLAN of the "
                             "vlans family; not yet verified by a live write"},
                # The upstream-queue bandwidth profile of the UNI must be set before a VLAN is
                # attached to its bridge port.
                {"section": "qos_interfaces.config", "kind": "uni",
                 "evidence": "live apply DS-LIN-TEST-01 2026-11-19: 'configure bridge port ... vlan-id 99' refused "
                             "with VLAN MGT error 277 (missing bandwidth profile on queue)"},
            ],
        },
    },
}
