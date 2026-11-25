# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the qos_interfaces family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "targeted_writes": True,
    "profile_references": "qos_profiles",
    "sections": {
        "config": {
            "identity": "name",
            "object": "qos_interface",
            # Live-verified on DS-LIN-TEST-01 (R6.2): the device creates the vlan: entry itself, at
            # exactly this default, when a VLAN joins the bridge port of a UNI. Live read
            # 2026-11-25: all 30 port VLANs on UNIs have one; none of the 329 on DSL lines and
            # link aggregation groups has.
            "created_with": [
                {
                    "prefix": "vlan:", "object": "vlan_port",
                    "default": {
                        "ds_num_queue": "not-applicable", "ds_num_rem_queue": "not-applicable",
                        "us_num_queue": "not-applicable", "gem_sharing": "not-applicable",
                        "mc_scheduler_node": "none", "bc_scheduler_node": "none",
                    },
                },
            ],
        },
    },
}
