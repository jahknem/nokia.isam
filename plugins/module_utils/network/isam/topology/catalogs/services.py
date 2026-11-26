"""Service configuration ownership and explicit shared-profile references."""

BINDINGS = (
    ("link_agg", "groups", "lag"),
    ("link_agg", "ports", "ethernet_port"),
    # STP port config is addressed by the aggregate's interface index (MSTP
    # Commands 55.5) and belongs to the port object, not the bridge port:
    # live counterexample xstp 1/1/8/6 has a LAG but no bridge-port interface.
    ("xstp", "ports", "port_layer"),
    ("qos_tca", "config", "qos_tca"),
    ("trouble_shooting_pon", "interfaces", "pon"),
    ("trouble_shooting_pon", "threshold.interfaces", "pon"),
    ("interfaces", "config", "interface"),
    ("bridges", "port", "bridge_port"),
    ("qos_interfaces", "config", "qos_interface"),
    ("isam_dhcp_relay", "config", "qos_interface"),
    ("isam_arp_relay", "config", "interface"),
    ("efm_oam_interface", "config", "user_port"),
    ("l2cp_user_port", "config", "user_port"),
    ("qos_profiles", "config", "qos_profile"),
)

# Canonical option name -> target profile type, NOT a suffix/name heuristic.
# Lists/dicts under a resource instance (queues etc.) use the same typed fields.
_QOS_REFERENCES = {
    "scheduler_node": "scheduler-node", "mc_scheduler_node": "scheduler-node", "bc_scheduler_node": "scheduler-node",
    "cac_profile": "cac", "ext_cac": "cac", "queue_profile": "queue", "shaper_profile": "shaper",
    "dsfld_shaper_prof": "shaper", "bandwidth_profile": "bandwidth", "ext_bw": "bandwidth",
    "ingress_profile": "ingress-qos", "aggr_usq_profile": "aggrqueuesconfig", "aggr_dsq_profile": "aggrqueuesconfig",
    "up_policer": "policer", "down_policer": "policer", "up_marker": "marker-d1p",
}
_QOS_REFERENCES.update({"q%d_%s" % (index, suffix): kind for index in range(8)
                        for suffix, kind in (("queue_prof", "queue"), ("shaper_prof", "shaper"), ("bandwidth_prof", "bandwidth"))})
PROFILE_REFERENCES = {"qos_interfaces": dict(_QOS_REFERENCES), "qos_profiles": dict(_QOS_REFERENCES)}
