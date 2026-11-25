# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""The device objects of an ISAM and what each directly contains.

No resource family owns these: an ONT is configured by several families, and one
family (interfaces, qos_interfaces) addresses several kinds of object. A family
states which object its instances address in relations/<family>.py ("object");
how an address is decoded into kind and parent is in identity.py.

Pure data without imports.

kind -> {children: the kinds it directly contains, status, ...}
  removal: what removing the object does on the device, with its evidence:
    removes_children  removing it removes everything it contains and every entry the
                      device created with it (no separate removal needed or possible)
    needs             the state the object must be in to be removed
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

# Child enumeration is NOT implemented by a targeted parent read. In particular,
# equipment ont interface <id> does not enumerate its sibling CLI slot nodes.
OBJECTS = {
    "msan": {"children": ["rack", "card", "applique"], "status": "unimplemented"},
    "applique": {"children": ["transceiver", "uplink"], "status": "unimplemented"},
    "rack": {"children": ["shelf"], "status": "unimplemented"},
    "shelf": {"children": ["card"], "status": "unimplemented"},
    "card": {"children": ["pon", "xdsl_line", "ethernet_port", "uplink", "ihub_port", "cage", "transceiver", "bonding_group", "lag",
                          "channel_pair"],
             "status": "unimplemented"},
    "ont": {"children": ["ont_slot"], "status": "unimplemented",
            "removal": {"removes_children": True, "needs": "admin-state down",
                        "evidence": "live write DS-LIN-TEST-01 2026-11-25, scratch ONT 1/1/6/7/10: 'no interface' on an admin-up ONT refused (Not in admin down state "
                                    "to delete); on an admin-down ONT it removed slot, UNI, bridge port, VLAN "
                                    "ports and every device-created entry"}},
    "ont_slot": {"children": ["uni"], "status": "unimplemented",
                 # The UNIs of a slot exist with the slot: no command creates or removes a UNI.
                 "removal": {"removes_children": True, "needs": "admin-state down (of the slot itself)",
                             "evidence": "live write DS-LIN-TEST-01 2026-11-25, scratch ONT 1/1/6/7/10: 'no slot' refused while the slot is admin-up, even on an "
                                         "admin-down ONT; with the slot admin-down it removed the UNI's "
                                         "ethernet ont, uni: interface and QoS entries"}},
    "pon": {"children": ["ont"], "status": "unimplemented"},
    "uni": {"children": ["bridge_port"], "status": "unimplemented"},
    "xdsl_line": {"children": ["bridge_port"], "status": "unimplemented"},
    "ethernet_port": {"children": ["bridge_port"], "status": "unimplemented"},
    # IHUB optical faceplate ports, not an assertion about their configured role.
    # Access bridge/VLAN layers do not establish IHUB service relationships.
    "uplink": {"children": [], "status": "leaf", "configuration_status": "partial",
               "limitation": "ihub_configuration_is_read_only_whole_source_projection_not_complete_recursive_coverage"},
    # Live stack evidence: bonding groups never carry bridge ports (their stack
    # lower is no-interface), so they have no VLAN-port descendants either.
    "bonding_group": {"children": [], "status": "leaf"},
    # The device keeps one LAG per Ethernet port, at the port's index (see relations/link_agg.py).
    "lag": {"children": ["bridge_port"], "status": "unimplemented"},
    "bridge_port": {"children": ["vlan_port"], "status": "unimplemented",
                    "removal": {"removes_children": True,
                                "evidence": "live write DS-LIN-TEST-01 2026-11-25, scratch ONT 1/1/6/7/10: 'bridge no port' with a VLAN attached removed the VLAN port's "
                                            "interface and QoS entries with it"}},
    "channel_pair": {"children": [], "status": "leaf"},
    "cage": {"children": [], "status": "leaf"},
    "transceiver": {"children": [], "status": "leaf"},
    "vlan_port": {"children": [], "status": "leaf"},
    "qos_profile": {"children": [], "status": "leaf"},
    "shared_profile": {"children": [], "status": "leaf"},
    "device_settings": {"children": [], "status": "leaf"},
    # IHUB objects: whole-family read units, their configuration is only partly modeled.
    "ihub_port": {"children": [], "configuration_status": "partial"},
    "ihub_virtual_port": {"children": [], "configuration_status": "partial"},
    "ihub_lag": {"children": [], "configuration_status": "partial"},
    "ihub_service": {"children": [], "configuration_status": "partial"},
    "ihub_customer": {"children": [], "configuration_status": "partial"},
}
