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
            # Values the device shows in the configuration of a kind but refuses to set there:
            # never written. Live 2026-11-25: every LAG of card 8 shows ds-num-queue 8, and
            # replaying it on LAG 1/1/8/6 is refused with QOS MGT error 45 (only per PON).
            "read_only": {"user_port": ["ds_num_queue"]},
            # Attributes an interface kind never accepts, whatever else is configured: every
            # attribute of the device syntax tried on each kind (live write DS-LIN-TEST-01
            # 2026-11-25: scratch ONT 1/1/6/7/10 with UNI and VLAN port, PON 1/1/6/16, DSL line
            # 1/1/3/48, LAG 1/1/8/6; configured interfaces restored and read back identical).
            # Only refusals whose reason is the interface type are listed; those that depend on
            # state (queues in use, VLANs, scheduler mode) or on a profile's content are not.
            # "user_port" is a bare port address: the DSL line and the LAG refuse exactly the
            # same. The module refuses these before writing, so check mode reports them.
            "refuses": {
                "ont": {
                    "aggr_dsq_profile": "QOS MGT error 203: The AggrQueuesConfig profile can only be supported on UNI",
                    "aggr_usq_profile": "QOS MGT error 203: The AggrQueuesConfig profile can only be supported on UNI",
                    "autoschedule": "QOS MGT error 96: AutoSchedule cannot be assigned to this interface type",
                    "bandwidth_profile": "QOS MGT error 202: The BW profile/Sharing can only be supported on UNI or US queues",
                    "bandwidth_sharing": "QOS MGT error 202: The BW profile/Sharing can only be supported on UNI or US queues",
                    "bc_scheduler_node": "QOS MGT error 175: The interface does not support configure PON Shared Service Broadcast Scheduler Profile",
                    "cac_profile": "QOS MGT error 42: CAC Profile cannot be assigned to this Interface Type",
                    "ds_num_queue": "QOS MGT error 45: Number of Downstream Qs per Line can be configured only on a per PON basis",
                    "ds_schedule_tag": "QOS MGT error 218: The interface does not support configure scheduler tag",
                    "dsfld_shaper_prof": "QOS MGT error 129: Non Zero DS Flooding shaper profile is only allowed for PON",
                    "ext_cac": "QOS MGT error 42: CAC Profile cannot be assigned to this Interface Type",
                    "gem_sharing": "QOS MGT error 126: GEM Sharing is not applicable for this type of interface",
                    "mc_scheduler_node": "QOS MGT error 174: The interface does not support configure PON Shared Service Multicast Scheduler Profile",
                    "scheduler_mode": "QOS MGT error 173: The interface does not support configure PON scheduler mode",
                },
                "uni": {
                    "autoschedule": "QOS MGT error 96: AutoSchedule cannot be assigned to this interface type",
                    "bc_scheduler_node": "QOS MGT error 175: The interface does not support configure PON Shared Service Broadcast Scheduler Profile",
                    "ds_num_queue": "QOS MGT error 45: Number of Downstream Qs per Line can be configured only on a per PON basis",
                    "ds_num_rem_queue": "QOS MGT error 114: Number of Downstream Remote Qs per Line can be configured only on a per ONT basis",
                    "ds_queue_sharing": "QOS MGT error 46: Q Sharing can only be enabled on ONT",
                    "ds_schedule_tag": "QOS MGT error 218: The interface does not support configure scheduler tag",
                    "dsfld_shaper_prof": "QOS MGT error 129: Non Zero DS Flooding shaper profile is only allowed for PON",
                    "ext_cac": "QOS MGT error 42: CAC Profile cannot be assigned to this Interface Type",
                    "mc_scheduler_node": "QOS MGT error 174: The interface does not support configure PON Shared Service Multicast Scheduler Profile",
                    "scheduler_mode": "QOS MGT error 173: The interface does not support configure PON scheduler mode",
                    "us_num_queue": "QOS MGT error 48: Number of Upstream Qs per Uni can be configured only for ONT",
                    "us_queue_sharing": "QOS MGT error 46: Q Sharing can only be enabled on ONT",
                    "us_vlanport_queue": "QOS MGT error 116: us-vlanport-queues can only be enabled on an ONT interface",
                },
                "vlan_port": {
                    "aggr_dsq_profile": "QOS MGT error 120: Attribute not supported for this interface",
                    "aggr_usq_profile": "QOS MGT error 120: Attribute not supported for this interface",
                    "autoschedule": "QOS MGT error 120: Attribute not supported for this interface",
                    "bandwidth_profile": "QOS MGT error 120: Attribute not supported for this interface",
                    "bandwidth_sharing": "QOS MGT error 120: Attribute not supported for this interface",
                    "bc_scheduler_node": "QOS MGT error 120: Attribute not supported for this interface",
                    "cac_profile": "QOS MGT error 120: Attribute not supported for this interface",
                    "ds_num_queue": "QOS MGT error 120: Attribute not supported for this interface",
                    "ds_num_rem_queue": "QOS MGT error 120: Attribute not supported for this interface",
                    "ds_queue_sharing": "QOS MGT error 120: Attribute not supported for this interface",
                    "ds_schedule_tag": "QOS MGT error 120: Attribute not supported for this interface",
                    "dsfld_shaper_prof": "QOS MGT error 120: Attribute not supported for this interface",
                    "ext_cac": "QOS MGT error 120: Attribute not supported for this interface",
                    "gem_sharing": "QOS MGT error 120: Attribute not supported for this interface",
                    "mc_scheduler_node": "QOS MGT error 120: Attribute not supported for this interface",
                    "queue_stats_on": "QOS MGT error 120: Attribute not supported for this interface",
                    "scheduler_mode": "QOS MGT error 120: Attribute not supported for this interface",
                    "scheduler_node": "QOS MGT error 120: Attribute not supported for this interface",
                    "us_num_queue": "QOS MGT error 120: Attribute not supported for this interface",
                    "us_queue_sharing": "QOS MGT error 120: Attribute not supported for this interface",
                    "us_vlanport_queue": "QOS MGT error 120: Attribute not supported for this interface",
                },
                "pon": {
                    "aggr_dsq_profile": "QOS MGT error 203: The AggrQueuesConfig profile can only be supported on UNI",
                    "bandwidth_profile": "QOS MGT error 202: The BW profile/Sharing can only be supported on UNI or US queues",
                    "bandwidth_sharing": "QOS MGT error 202: The BW profile/Sharing can only be supported on UNI or US queues",
                    "ds_num_rem_queue": "QOS MGT error 114: Number of Downstream Remote Qs per Line can be configured only on a per ONT basis",
                    "ds_queue_sharing": "QOS MGT error 46: Q Sharing can only be enabled on ONT",
                    "ext_cac": "QOS MGT error 42: CAC Profile cannot be assigned to this Interface Type",
                    "gem_sharing": "QOS MGT error 126: GEM Sharing is not applicable for this type of interface",
                    "scheduler_node": "QOS MGT error 49: SchedulerNode Profile can be configured on ONT and UNI interfaces only",
                    "us_num_queue": "QOS MGT error 48: Number of Upstream Qs per Uni can be configured only for ONT",
                    "us_queue_sharing": "QOS MGT error 46: Q Sharing can only be enabled on ONT",
                    "us_vlanport_queue": "QOS MGT error 116: us-vlanport-queues can only be enabled on an ONT interface",
                },
                "user_port": {
                    "aggr_dsq_profile": "QOS MGT error 203: The AggrQueuesConfig profile can only be supported on UNI",
                    "autoschedule": "QOS MGT error 96: AutoSchedule cannot be assigned to this interface type",
                    "bandwidth_profile": "QOS MGT error 202: The BW profile/Sharing can only be supported on UNI or US queues",
                    "bandwidth_sharing": "QOS MGT error 202: The BW profile/Sharing can only be supported on UNI or US queues",
                    "bc_scheduler_node": "QOS MGT error 175: The interface does not support configure PON Shared Service Broadcast Scheduler Profile",
                    "ds_num_queue": "QOS MGT error 45: Number of Downstream Qs per Line can be configured only on a per PON basis",
                    "ds_num_rem_queue": "QOS MGT error 114: Number of Downstream Remote Qs per Line can be configured only on a per ONT basis",
                    "ds_queue_sharing": "QOS MGT error 46: Q Sharing can only be enabled on ONT",
                    "ds_schedule_tag": "QOS MGT error 218: The interface does not support configure scheduler tag",
                    "dsfld_shaper_prof": "QOS MGT error 129: Non Zero DS Flooding shaper profile is only allowed for PON",
                    "ext_cac": "QOS MGT error 42: CAC Profile cannot be assigned to this Interface Type",
                    "gem_sharing": "QOS MGT error 126: GEM Sharing is not applicable for this type of interface",
                    "mc_scheduler_node": "QOS MGT error 174: The interface does not support configure PON Shared Service Multicast Scheduler Profile",
                    "scheduler_mode": "QOS MGT error 173: The interface does not support configure PON scheduler mode",
                    "us_num_queue": "QOS MGT error 48: Number of Upstream Qs per Uni can be configured only for ONT",
                    "us_queue_sharing": "QOS MGT error 46: Q Sharing can only be enabled on ONT",
                    "us_vlanport_queue": "QOS MGT error 116: us-vlanport-queues can only be enabled on an ONT interface",
                },
            },
        },
    },
}
