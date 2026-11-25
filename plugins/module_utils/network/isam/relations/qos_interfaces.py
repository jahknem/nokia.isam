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
            # The index is the physical port or la-group of a user port (device help); the
            # device accepts only the bare form (xdsl-line:, bonding:, la-group: are invalid
            # tokens, read 2026-11-25), so a bare DSL address is the line, never its bonding group.
            "identity": "name",
            "object": "qos_interface",
            # The device creates these entries itself; an entry equal to its default was not
            # customized. Live write DS-LIN-TEST-01 2026-11-25 (scratch ONT 1/1/6/7/10): the ont:
            # entry appears with the ONT, the UNI entry with the ONT slot, the vlan: entry when a
            # VLAN joins the bridge port of a UNI. Live read 2026-11-25: all 30 port VLANs on UNIs
            # have a vlan: entry, none of the 329 on DSL lines and link aggregation groups has.
            "created_with": [
                {
                    "prefix": "ont:", "object": "ont",
                    "default": {
                        "ds_num_queue": "not-applicable", "ds_num_rem_queue": "not-applicable",
                        "gem_sharing": "not-applicable", "mc_scheduler_node": "none", "bc_scheduler_node": "none",
                    },
                },
                # Scheduler node, CAC profile and queues come from a per-card default (NGLT_Default,
                # FD_ONTUniVideo on the lab's GPON card); not recorded, so never treated as default.
                {"prefix": None, "object": "uni", "default": None},
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
