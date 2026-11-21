"""Equipment ownership. Identity fields remain authoritative in TARGETED_GATHER."""

# (resource, instance list, identity decoder). Only immediate ownership is declared.
BINDINGS = (
    ("isam_equipment", "racks", "rack"),
    ("isam_equipment", "shelves", "shelf"),
    ("isam_equipment", "slots", "card"),
    ("isam_equipment", "appliques", "applique"),
    ("interface_cages", "config", "cage"),
    ("isam_equipment", "diagnostics_sfp", "transceiver"),
    ("equipment_onts", "interfaces", "ont"),
    ("equipment_onts", "slots", "ont_slot"),
    ("equipment_onts", "loops", "ont"),
    ("equipment_onts", "pm_collects", "ont"),
)

# Child enumeration is NOT implemented by a targeted parent read. In particular,
# equipment ont interface <id> does not enumerate its sibling CLI slot nodes.
DISCOVERY = {
    "msan": {"children": ["rack", "card", "applique"], "status": "unimplemented"},
    "applique": {"children": ["transceiver", "uplink"], "status": "unimplemented"},
    "rack": {"children": ["shelf"], "status": "unimplemented"},
    "shelf": {"children": ["card"], "status": "unimplemented"},
    "card": {"children": ["pon", "xdsl_line", "ethernet_port", "uplink", "cage", "transceiver", "bonding_group", "lag",
                          "channel_pair"],
             "status": "unimplemented"},
    "ont": {"children": ["ont_slot"], "status": "unimplemented"},
    "ont_slot": {"children": ["uni"], "status": "unimplemented"},
}
