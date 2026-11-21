"""Access objects across CLI branches; bindings use the existing canonical facts."""

BINDINGS = (
    ("pon_interfaces", "config", "pon"),
    # EPON interface configuration is addressed by the PON index
    # (rack/shelf/slot/PonId, Epon Configuration Commands 69.2).
    ("epon_interfaces", "config", "pon"),
    # NGPON2 channel pairs are wavelength interfaces on the LT slot
    # (rack/shelf/slot/ChannelPairId, Channel Pair Commands 68.4). Channel-group
    # membership is a logical association, not physical containment.
    ("channel_pair_pm", "config", "channel_pair"),
    ("ani_onts", "config", "ont"),
    ("ntp_onts", "config", "ont"),
    ("xdsl_onts", "config", "ont"),
    ("ethernet_onts", "config", "uni"),
    ("uni_onts", "config", "uni"),
    ("l2uni_onts", "performance_monitor", "uni"),
    ("l2uni_onts", "tc_layer_threshold", "uni"),
    ("xdsl_boards", "boards", "lt_card"),
    ("xdsl_boards", "vp_boards", "lt_card"),
    ("xdsl_lines", "config", "xdsl_line"),
    ("xdsl_inm", "far_end", "xdsl_line"),
    ("xdsl_inm", "near_end", "xdsl_line"),
    ("ethernet_line", "config", "ethernet_port"),
    ("xdsl_bonding", "boards", "lt_card"),
    ("xdsl_bonding", "groups", "bonding_group"),
    ("qos_global", "line_cards", "card"),
    ("isam_ipv6_antispoofing_slot", "config", "lt_card"),
    # PPPoE client interfaces and PPPoE-L2 statistics are per vlan-port
    # (PPPoE Commands 32.3 / PPPoEL2STATS 33.2). ATM vpi:vci and ng2 identity
    # variants are not decoded yet and remain explicit per-instance gaps.
    ("pppoe_client_interface", "config", "interface"),
    ("pppoel2_statistics", "config", "interface"),
    # NT-slot security settings only address nt-a/nt-b (Security Commands 16.42).
    ("isam_system_security", "slots", "card"),
    # 802.1X authenticator ports use the user-port identity superset; ONT
    # voip/vuni/LLId and ng2 variants stay explicit per-instance gaps.
    ("isam_system_security", "pae.ports", "user_port"),
    # SSM output per SyncE faceplate port: nt-a/nt-b/ntio cage identities
    # (System Commands 15.35). The active-NT alias (nt:...) has no fixed owner.
    ("system", "sync_if_timing.ssmout_synce", "transceiver"),
)

DISCOVERY = {
    "pon": {"children": ["ont"], "status": "unimplemented"},
    "uni": {"children": ["bridge_port"], "status": "unimplemented"},
    "xdsl_line": {"children": ["bridge_port"], "status": "unimplemented"},
    "ethernet_port": {"children": ["bridge_port"], "status": "unimplemented"},
    # IHUB optical faceplate ports, not an assertion about their configured role.
    # Access bridge/VLAN layers do not establish IHUB service relationships.
    "uplink": {"children": [], "status": "leaf", "configuration_status": "unmodeled",
               "limitation": "ihub_port_identity_and_discovery_need_evidence_separate_from_access_interface_cli"},
    # Live stack evidence: bonding groups never carry bridge ports (their stack
    # lower is no-interface), so they have no VLAN-port descendants either.
    "bonding_group": {"children": [], "status": "leaf"},
    "lag": {"children": ["bridge_port"], "status": "unimplemented"},
    "bridge_port": {"children": ["vlan_port"], "status": "unimplemented"},
    "channel_pair": {"children": [], "status": "leaf"},
    "cage": {"children": [], "status": "leaf"},
    "transceiver": {"children": [], "status": "leaf"},
    "vlan_port": {"children": [], "status": "leaf"},
    "qos_profile": {"children": [], "status": "leaf"},
    "shared_profile": {"children": [], "status": "leaf"},
    "device_settings": {"children": [], "status": "leaf"},
}
