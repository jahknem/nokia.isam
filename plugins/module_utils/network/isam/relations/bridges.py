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
        # A port joins only an existing VLAN: the forwarding VLAN (l2fwder_vlan) when the entry
        # names one, otherwise the VLAN id itself. Live read 2026-11-25 on DS-LIN-TEST-01: all
        # 359 port VLANs resolve to a VLAN of the vlans family that way. Not yet written live.
        "port": {"identity": "port", "object": "bridge_port", "creates": True, "requires": ["vlans.config"]},
    },
}
