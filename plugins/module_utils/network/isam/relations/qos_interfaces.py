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
            # tokens, read 2026-11-25). A bare DSL address is the line, never its bonding group;
            # a bare Ethernet-card address is the LAG the device keeps there (live write
            # 2026-11-25, QOS MGT error 216 once the port's LAG has no physical port).
            "identity": "name",
            "object": "qos_interface",
            # The device creates these entries itself; an entry equal to its default was not
            # customized. Live write DS-LIN-TEST-01 2026-11-25 (scratch ONT 1/1/6/7/10): the ont:
            # entry appears with the ONT, the UNI entry with the ONT slot, the vlan: entry when a
            # VLAN joins the bridge port of a UNI. Live read 2026-11-25: all 30 port VLANs on UNIs
            # have a vlan: entry, none of the 329 on DSL lines and link aggregation groups has;
            # every PON (64 of 64, also on card 6 without a board) and every DSL line (96 of 96)
            # has its entry.
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
                {"prefix": "pon:", "object": "pon", "default": None},
                {"prefix": None, "object": "xdsl_line", "default": None},
                {"prefix": None, "object": "lag", "default": None},
            ],
            # Settings that can only be changed while something else does not exist yet, or
            # that need another setting first (live write DS-LIN-TEST-01 2026-11-25, docs/live-validation-2026-11-25.md).
            # In creation order they hold; changing them later means removing what blocks them.
            "requires": [
                {"section": "qos_interfaces.config", "kind": "ont", "for": "vlan_port",
                 "evidence": "live write DS-LIN-TEST-01 2026-11-25: VLAN-port upstream queues refused (QOS MGT error 117) unless the ONT has "
                             "us-vlanport-queue; us-vlanport-queue cannot change once VLANs exist on the ONT (error "
                             "119) and excludes us-queue-sharing (error 143)"},
                {"section": "qos_interfaces.config", "kind": "ont", "for": "uni",
                 "evidence": "live write DS-LIN-TEST-01 2026-11-25: us-queue-sharing cannot change while an upstream queue of the ONT is in use "
                             "(QOS MGT error 81)"},
            ],
            # Attributes an interface kind never accepts, whatever else is configured
            # (live write DS-LIN-TEST-01 2026-11-25, scratch ONT 1/1/6/7/10 and PON 1/1/6/16). Conditional refusals
            # (scheduler mode, existing VLANs or slots) are not listed. The module refuses these
            # before writing, so check mode reports what the device would refuse.
            "refuses": {
                "ont": {
                    "autoschedule": "QOS MGT error 96: AutoSchedule cannot be assigned to this interface type",
                    "ds_num_queue": "QOS MGT error 45: number of downstream queues only per PON",
                    "gem_sharing": "QOS MGT error 126: GEM sharing is not applicable for this type of interface",
                    "mc_scheduler_node": "QOS MGT error 174: multicast scheduler profile not supported",
                    "bc_scheduler_node": "QOS MGT error 175: broadcast scheduler profile not supported",
                    "cac_profile": "QOS MGT error 42: CAC profile cannot be assigned to this interface type",
                },
                "uni": {
                    "ds_queue_sharing": "QOS MGT error 46: queue sharing only on an ONT",
                    "us_queue_sharing": "QOS MGT error 46: queue sharing only on an ONT",
                    "autoschedule": "QOS MGT error 96: AutoSchedule cannot be assigned to this interface type",
                    "us_vlanport_queue": "QOS MGT error 116: us-vlanport-queues only on an ONT interface",
                    "ds_num_queue": "QOS MGT error 45: number of downstream queues only per PON",
                    "us_num_queue": "QOS MGT error 48: number of upstream queues only for an ONT",
                    "mc_scheduler_node": "QOS MGT error 174: multicast scheduler profile not supported",
                    "bc_scheduler_node": "QOS MGT error 175: broadcast scheduler profile not supported",
                },
                "vlan_port": {
                    field: "QOS MGT error 120: attribute not supported for a VLAN port" for field in (
                        "scheduler_node", "cac_profile", "ds_queue_sharing", "us_queue_sharing", "autoschedule",
                        "us_vlanport_queue", "queue_stats_on", "ds_num_queue", "us_num_queue", "gem_sharing",
                        "mc_scheduler_node", "bc_scheduler_node", "bandwidth_profile")
                },
                "pon": {
                    "us_num_queue": "QOS MGT error 48: number of upstream queues only for an ONT",
                    "gem_sharing": "QOS MGT error 126: GEM sharing is not applicable for this type of interface",
                    "scheduler_node": "QOS MGT error 49: scheduler-node profile only on ONT and UNI interfaces",
                    "ds_queue_sharing": "QOS MGT error 46: queue sharing only on an ONT",
                },
            },
        },
    },
}
