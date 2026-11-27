# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the isam_dhcp_relay family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "targeted_writes": True,
    "sections": {
        # Per VLAN port (vlan:<port>:<vlan>; vlan-port: is an invalid token). Not observable:
        # switched on and off on a scratch VLAN port (PON 1/1/7/16, DS-LIN-TEST-01 2026-11-26),
        # every read answered the same in both states: 'info configure dhcp-relay port-stats
        # vlan:<vp> flat [detail]' (header only), the whole flat read (nothing), 'show
        # dhcp-relay port-stats <port>' (nothing) and '<port> vlan <vlan> [summary]'.
        "config": {"identity": "name", "object": "qos_interface", "kinds": ["vlan_port"], "observable": False},
    },
}
