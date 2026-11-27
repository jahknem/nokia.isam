# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the isam_arp_relay family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "targeted_writes": True,
    "sections": {
        # Per VLAN port ("configure arp-relay statistics (vlan-port)", ARP-RELAY 28.2). The
        # switch is an instance without attributes: the whole read never lists it, but its
        # single read answers "instance does not exist" when off and only the header when on;
        # 'show arp-relay-stats <port> vlan <vlan> extensive' prints counters only when on
        # (DS-LIN-TEST-01 2026-11-26, scratch VLAN ports on card 6 and PON 1/1/7/16).
        "config": {"identity": "name", "object": "interface", "kinds": ["vlan_port"]},
    },
}
