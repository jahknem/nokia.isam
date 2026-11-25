# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Relations of the qos_profiles family. Format: relations/README.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

RELATIONS = {
    "profile_references": "qos_profiles",
    # Option name -> the profile type it names, wherever the option occurs (also inside queues
    # and other lists of an instance). Typed by option, never by a name suffix. Families whose
    # options name QoS profiles declare "profile_references": "qos_profiles".
    "reference_fields": dict(
        {
            "scheduler_node": "scheduler-node", "mc_scheduler_node": "scheduler-node", "bc_scheduler_node": "scheduler-node",
            "cac_profile": "cac", "ext_cac": "cac", "queue_profile": "queue", "shaper_profile": "shaper",
            "dsfld_shaper_prof": "shaper", "bandwidth_profile": "bandwidth", "ext_bw": "bandwidth",
            "ingress_profile": "ingress-qos", "aggr_usq_profile": "aggrqueuesconfig", "aggr_dsq_profile": "aggrqueuesconfig",
            "up_policer": "policer", "down_policer": "policer", "up_marker": "marker-d1p",
        },
        **{"q%d_%s" % (index, suffix): kind for index in range(8)
           for suffix, kind in (("queue_prof", "queue"), ("shaper_prof", "shaper"), ("bandwidth_prof", "bandwidth"))}
    ),
    "sections": {
        "config": {"identity": ["profile_type", "name"], "object": "qos_profile", "scope": "shared_profile"},
    },
}
