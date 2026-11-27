# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the pppoel2_statistics family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "sections": {
        # Per vlan-port (PPPoEL2STATS 33.2).
        "config": {"identity": "name", "object": "interface", "kinds": ["vlan_port"]},
    },
}
