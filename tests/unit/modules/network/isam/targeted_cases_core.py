"""Targeted gathering cases: ONT, UNI, PON, bridge, QoS, relay and equipment resources."""

ONT, SIB = "1/1/5/1/3", "1/1/5/1/30"
UNI, SIB_UNI = ONT + "/1/1", SIB + "/1/1"


def case(module, config, lines, sibling_config, sibling, marker, sibling_marker):
    return {"module": module, "config": config, "lines": lines, "sibling_config": sibling_config,
            "sibling": sibling, "marker": marker, "sibling_marker": sibling_marker}


def ont_case(module, make_config, make_lines, unit=ONT, sibling_unit=SIB):
    """Target and neighbour differ only in the ONT/UNI index."""
    # The ONT index is a prefix of its neighbour's: match it with the opening quote.
    markers = ("'%s" % unit, "'%s" % sibling_unit) if unit == ONT else (unit, sibling_unit)
    return case(module, make_config(unit), make_lines(unit), make_config(sibling_unit), make_lines(sibling_unit), *markers)


CASES = {
    "ani_onts": ont_case("isam_ani_onts", lambda o: [{"ont_idx": o}],
                         lambda o: ["configure ani ont tca-thresh %s lower-optical-th -28" % o]),
    "bridges": ont_case("isam_bridges", lambda u: {"port": [{"port": u}]},
                        lambda u: ["configure bridge port %s max-unicast-mac 5 pvid 99" % u, "configure bridge port %s vlan-id 99" % u],
                        UNI, SIB_UNI),
    "efm_oam_interface": ont_case("isam_efm_oam_interface", lambda u: [{"name": u}],
                                  lambda u: ["configure efm-oam interface %s admin-up keep-alive-intvl 10" % u], UNI, SIB_UNI),
    "equipment_onts:interfaces": ont_case("isam_equipment_onts", lambda o: {"interfaces": [{"ont_idx": o}]},
                                          lambda o: ["configure equipment ont interface %s sw-ver-pland auto admin-state up" % o]),
    "equipment_onts:slots": ont_case("isam_equipment_onts", lambda o: {"slots": [{"ont_slot_idx": o + "/1"}]},
                                     lambda o: ["configure equipment ont slot %s/1 planned-card-type ethernet plndnumdataports 1 plndnumvoiceports 0" % o]),
    "equipment_onts:sw_ctrls": case("isam_equipment_onts", {"sw_ctrls": [{"sw_ctrl_id": "7"}]},
                                    ["configure equipment ont sw-ctrl 7 hw-version 3FE49 plnd-sw-version 3FE4"],
                                    {"sw_ctrls": [{"sw_ctrl_id": "8"}]},
                                    ["configure equipment ont sw-ctrl 8 hw-version 3FE50 plnd-sw-version 3FE5"],
                                    "3FE49", "3FE50"),
    "ethernet_onts": ont_case("isam_ethernet_onts", lambda u: [{"uni_idx": u}],
                              lambda u: ["configure ethernet ont %s auto-detect auto admin-state up" % u], UNI, SIB_UNI),
    "interfaces": ont_case("isam_interfaces", lambda u: [{"name": "uni:" + u}],
                           lambda u: ["configure interface port uni:%s admin-up" % u], UNI, SIB_UNI),
    "isam_arp_relay": ont_case("isam_arp_relay", lambda u: [{"name": "vlan-port:%s:10" % u}],
                               lambda u: ["configure arp-relay statistics vlan-port:%s:10" % u], UNI, SIB_UNI),
    "isam_dhcp_relay": ont_case("isam_dhcp_relay", lambda u: [{"name": "vlan-port:%s:10" % u}],
                                lambda u: ["configure dhcp-relay port-stats vlan-port:%s:10" % u], UNI, SIB_UNI),
    "isam_equipment:slots": case("isam_equipment", {"slots": [{"id": "lt:1/1/5"}]},
                                 ["configure equipment slot lt:1/1/5 planned-type fglt-b unlock"],
                                 {"slots": [{"id": "lt:1/1/30"}]},
                                 ["configure equipment slot lt:1/1/30 planned-type fglt-b unlock"], "lt:1/1/5'", "lt:1/1/30'"),
    "isam_equipment:shelves": case("isam_equipment", {"shelves": [{"id": "1/1"}]},
                                   ["configure equipment shelf 1/1 planned-type ralt-a"],
                                   {"shelves": [{"id": "1/2"}]},
                                   ["configure equipment shelf 1/2 planned-type ralt-b"], "ralt-a", "ralt-b"),
    "isam_equipment:appliques": case("isam_equipment", {"appliques": [{"id": "1/1/1"}]},
                                     ["configure equipment applique 1/1/1 planned-type ap-a"],
                                     {"appliques": [{"id": "1/1/2"}]},
                                     ["configure equipment applique 1/1/2 planned-type ap-b"], "ap-a", "ap-b"),
    "isam_equipment:protection_groups": case("isam_equipment", {"protection_groups": [{"id": "1"}]},
                                             ["configure equipment protection-group 1 admin-status unlock eps-quenchfactor 1000"],
                                             {"protection_groups": [{"id": "2"}]},
                                             ["configure equipment protection-group 2 admin-status lock eps-quenchfactor 2000"],
                                             "1000", "2000"),
    "ntp_onts": ont_case("isam_ntp_onts", lambda o: [{"ont_id": o}], lambda o: ["configure ntp ont %s client-state on" % o]),
    "pon_interfaces": case("isam_pon_interfaces", [{"name": "1/1/5/3"}], ["configure pon interface 1/1/5/3 admin-state up"],
                           [{"name": "1/1/5/30"}], ["configure pon interface 1/1/5/30 admin-state up"], "1/1/5/3'", "1/1/5/30'"),
    "qos_interfaces": ont_case("isam_qos_interfaces", lambda u: [{"name": u}],
                               lambda u: ["configure qos interface %s scheduler-node name:A" % u], UNI, SIB_UNI),
}
