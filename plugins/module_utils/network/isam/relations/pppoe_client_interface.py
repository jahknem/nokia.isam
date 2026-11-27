# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the pppoe_client_interface family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "sections": {
        # PPPoE client interfaces and PPPoE-L2 statistics are per vlan-port
        # (PPPoE Commands 32.3 / PPPoEL2STATS 33.2). ATM vpi:vci and ng2 identity
        # variants are not decoded yet and remain explicit per-instance gaps.
        "config": {"identity": "name", "object": "interface", "kinds": ["vlan_port"],
                   "references": {"profile_name": "pppoe_client_ppp_profile.config"}},
    },
}
