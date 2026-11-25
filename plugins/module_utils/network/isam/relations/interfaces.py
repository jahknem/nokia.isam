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
            # The device creates these entries itself: ont: with the ONT, uni: with the ONT slot,
            # vlan-port: when a VLAN joins a bridge port (live write DS-LIN-TEST-01 2026-11-25,
            # scratch ONT 1/1/6/7/10). A differing entry was customized. Live read 2026-11-25: 359
            # of 359 port VLANs have their vlan-port: entry, none exists without one.
            "created_with": [
                # admin-up follows the ONT's admin state (down at creation, up with it): this
                # default holds for an admin-up ONT.
                {"prefix": "ont:", "object": "ont", "default": {"admin_up": True, "link_updown_trap": True}},
                {"prefix": "uni:", "object": "uni", "default": None},
                {
                    "prefix": "vlan-port:", "object": "vlan_port",
                    "default": {"admin_up": True, "link_updown_trap": False, "severity": "no-value"},
                },
            ],
        },
    },
}
