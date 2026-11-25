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
                 "evidence": "live write DS-LIN-TEST-01 2026-11-25: vlan-id of a VLAN the vlans family lacks is "
                             "refused with VLAN MGT error 81 (L2-forwarder not created yet); live read: all 359 "
                             "port VLANs resolve to a VLAN of the vlans family"},
                # The upstream-queue bandwidth profile of the UNI must be set before a VLAN is
                # attached to its bridge port.
                {"section": "qos_interfaces.config", "kind": "uni",
                 "evidence": "live writes DS-LIN-TEST-01 2026-11-19 and 2026-11-25: vlan-id before the UNI's "
                             "upstream-queue bandwidth profile is refused with VLAN MGT error 277; removing the "
                             "profile while the VLAN uses the queue is refused with QOS MGT error 135; "
                             "gem-sharing of the UNI cannot change once VLAN ports are attached (error 125)"},
            ],
        },
    },
}
