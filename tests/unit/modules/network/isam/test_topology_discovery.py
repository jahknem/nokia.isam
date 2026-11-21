"""Fresh child-enumeration contracts: success, absence, failure and coverage."""
import json

import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.discovery import (
    attach_discovery,
    coverage,
    enumerate_children,
    parse_ont_serials,
    parse_ont_slots,
    result,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.graph import build_graph, node_key
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.identity import UnknownIdentity

PON = "1/1/5/1"
ONT = PON + "/3"
SLOT = ONT + "/1"


def ont_table(*identities):
    lines = [
        "===================================================================================================================",
        "interface table",
        "===================================================================================================================",
        "             |            |          |actual   |              |             |            |cfgfile1|cfgfile2|actual ",
        "ont-idx      |eqpt-ver-num|sw-ver-act|num-slots|version-number|sernum       |yp-serial-no|ver-act |ver-act |us-rate",
        "-------------+------------+----------+---------+--------------+-------------+------------+--------+--------+-------",
    ]
    for identity in identities:
        lines.append("%-13s G2110BV2D0   AN03110R   1         G2110BV2D0     XXXX:SANIT  unknown                        1.25g  " % identity)
    lines.append("interface count : %d" % len(identities))
    return "\n".join(lines)


def slot_config(*identities):
    return "\n".join("configure equipment ont slot %s planned-card-type ethernet plndnumdataports 1" % i
                     for i in identities)


def test_successful_ont_enumeration_filters_device_wide_source_by_pon():
    # Source is device-wide: includes a sibling PON's ONT that must be filtered out.
    item = parse_ont_serials(ont_table(ONT, PON + "/1", "1/1/5/2/1"), PON)
    assert item["status"] == "ok"
    assert item["children"] == [PON + "/1", ONT]
    assert item["command"] == "show equipment ont interface"
    assert item["read_scope"] == "device"
    assert item["parent"] == node_key("pon", PON)
    json.dumps(item)


def test_empty_ont_table_confirms_absence_not_failure():
    item = parse_ont_serials(ont_table(), PON)
    assert item["status"] == "ok" and item["children"] == []


def test_ont_table_with_only_other_pons_confirms_absence_for_this_pon():
    item = parse_ont_serials(ont_table("1/1/5/2/1"), PON)
    assert item["status"] == "ok" and item["children"] == []


def test_malformed_ont_identity_is_rejected_not_filtered():
    with pytest.raises(UnknownIdentity):
        parse_ont_serials(ont_table("not-an-ont"), PON)


def test_slot_enumeration_filters_family_wide_source_by_ont():
    item = parse_ont_slots(slot_config(SLOT, ONT + "/2", "1/1/5/2/1/1"), ONT)
    assert item["children"] == [SLOT, ONT + "/2"]
    assert item["read_scope"] == "family"
    assert item["command"] == "info configure equipment ont flat"


def test_slot_enumeration_ignores_non_slot_nodes():
    text = "configure equipment ont interface %s desc1 x\n" % ONT + slot_config(SLOT)
    item = parse_ont_slots(text, ONT)
    assert item["children"] == [SLOT]


def test_malformed_slot_identity_is_rejected():
    with pytest.raises(UnknownIdentity):
        parse_ont_slots("configure equipment ont slot bad-id planned-card-type ethernet", ONT)


def test_failed_enumeration_cannot_report_children():
    with pytest.raises(ValueError):
        result("pon", PON, "ont", "error", children=[ONT], error="timeout")
    with pytest.raises(ValueError):
        result("pon", PON, "ont", "ok")
    with pytest.raises(ValueError):
        result("pon", PON, "ont", "ok", command="show equipment ont interface")  # missing read_scope
    item = result("pon", PON, "ont", "unsupported", error="command not supported")
    assert item["children"] == [] and item["status"] == "unsupported"


def test_child_must_belong_to_requested_parent():
    with pytest.raises(UnknownIdentity):
        result("pon", PON, "ont", "ok", children=["1/1/5/2/1"],
               command="show equipment ont interface", read_scope="device")


def graph():
    return build_graph({
        "equipment_onts": {"interfaces": [{"ont_idx": ONT}], "slots": [{"ont_slot_idx": SLOT}]},
        "pon_interfaces": [{"name": PON}],
    }, "M")


def test_coverage_requires_fresh_evidence_for_every_relation():
    g = graph()
    manifest = coverage(g, "pon", PON)
    assert manifest["complete"] is False
    assert {m["reason"] for m in manifest["missing"]} == {"discovery_missing"}
    # pon->ont, ont->ont_slot, ont_slot->uni (all implemented, none yet read)
    assert len(manifest["required"]) == 3
    assert manifest["unimplemented"] == []


def test_successful_discovery_certifies_only_the_enumerated_subtree():
    g = graph()
    g = attach_discovery(g, [
        parse_ont_serials(ont_table(ONT), PON),
        parse_ont_slots(slot_config(SLOT), ONT),
        enumerate_children("ont_slot", SLOT, "uni", "#----------------"),
    ])
    manifest = coverage(g, "pon", PON)
    assert manifest["complete"] is True
    assert manifest["failed"] == [] and manifest["missing"] == [] and manifest["unimplemented"] == []
    assert node_key("ont_slot", SLOT) in manifest["nodes"]
    assert all(r["read_scope"] in ("device", "family", "scoped") for r in manifest["ok"])


def test_failed_discovery_keeps_cached_children_visible_but_blocks_coverage():
    g = graph()
    g = attach_discovery(g, [
        parse_ont_serials(ont_table(ONT), PON),
        result("ont", ONT, "ont_slot", "error", error="timeout"),
    ])
    manifest = coverage(g, "pon", PON)
    assert manifest["complete"] is False
    assert manifest["failed"][0]["reason"] == "error"
    assert node_key("ont_slot", SLOT) in manifest["nodes"]


def test_new_child_from_discovery_is_added_to_the_graph():
    g = graph()
    new_ont = PON + "/4"
    g = attach_discovery(g, [parse_ont_serials(ont_table(ONT, new_ont), PON)])
    assert node_key("ont", new_ont) in {n["key"] for n in g["nodes"]}
    manifest = coverage(g, "pon", PON)
    assert manifest["complete"] is False  # new ONT still needs slot discovery


def test_duplicate_or_unknown_discovery_results_are_rejected():
    g = graph()
    item = parse_ont_serials(ont_table(ONT), PON)
    with pytest.raises(ValueError):
        attach_discovery(g, [item, item])
    bad = dict(item, parent=node_key("pon", "1/1/9/9"))
    with pytest.raises(ValueError):
        attach_discovery(g, [bad])


def test_unsupported_relation_is_not_silently_empty():
    g = graph()
    g = attach_discovery(g, [result("pon", PON, "ont", "unsupported", error="not supported")])
    manifest = coverage(g, "pon", PON)
    assert manifest["complete"] is False
    assert manifest["failed"][0]["reason"] == "unsupported"


# --- Source-driven adapters (card children, slot -> UNI) -----------------------

def test_uni_enumeration_filters_family_source_by_slot():
    cfg = ("configure ethernet ont 1/1/5/1/3/1/1 admin-state up\n"
           "configure ethernet ont 1/1/5/1/3/2/1 admin-state up\n"
           "configure ethernet ont 1/1/5/1/6/1/1 admin-state up\n")
    item = enumerate_children("ont_slot", SLOT, "uni", cfg)
    assert item["status"] == "ok" and item["read_scope"] == "family"
    assert item["children"] == [SLOT + "/1"]
    assert item["command"] == "info configure ethernet ont flat"


def test_card_children_filter_each_source_by_card():
    pon_cfg = ("configure pon interface 1/1/2/1 admin-state up\n"
               "configure pon interface 1/1/2/2 admin-state up\n"
               "configure pon interface 1/1/3/1 admin-state up\n")
    assert enumerate_children("card", "lt:1/1/2", "pon", pon_cfg)["children"] == ["1/1/2/1", "1/1/2/2"]
    xdsl_cfg = "configure xdsl line 1/1/3/1 service-profile 13\nconfigure xdsl line 1/1/4/1 service-profile 13\n"
    assert enumerate_children("card", "lt:1/1/3", "xdsl_line", xdsl_cfg)["children"] == ["1/1/3/1"]
    eth_cfg = "configure ethernet line 1/1/8/1 port-type uni\nconfigure ethernet line 1/1/9/1 port-type uni\n"
    assert enumerate_children("card", "lt:1/1/8", "ethernet_port", eth_cfg)["children"] == ["1/1/8/1"]
    cage_cfg = "configure interface cage lt:1/1/2:cage:1 description x\nconfigure interface cage lt:1/1/3:cage:1 description x\n"
    assert enumerate_children("card", "lt:1/1/2", "cage", cage_cfg)["children"] == ["lt:1/1/2:cage:1"]


def test_recognized_empty_source_confirms_absence_for_card_child():
    item = enumerate_children("card", "lt:1/1/2", "pon", "#----------------")
    assert item["status"] == "ok" and item["children"] == []


def test_malformed_child_identity_in_source_is_rejected():
    with pytest.raises(UnknownIdentity):
        enumerate_children("card", "lt:1/1/2", "pon", "configure pon interface bad-id admin-state up")


def test_unknown_child_kind_has_no_source():
    with pytest.raises(UnknownIdentity):
        enumerate_children("card", "lt:1/1/2", "not_a_child", "")


def test_unimplemented_relation_is_a_capability_gap_not_missing_read():
    # Controller-port discovery still needs live evidence; line/bonding/LAG
    # VLAN-port discovery is blocked by the bare-address attribution question.
    g = build_graph({"isam_equipment": {"slots": [{"id": "lt:1/1/2"}]}}, "M")
    manifest = coverage(g, "card", "lt:1/1/2")
    assert manifest["complete"] is False
    reasons = {u["child_kind"] for u in manifest["unimplemented"]}
    assert "uplink" in reasons
    # implemented-but-unread card children are 'missing', not 'unimplemented'
    assert {m["child_kind"] for m in manifest["missing"]} >= {"pon", "xdsl_line", "ethernet_port", "cage",
                                                              "transceiver", "channel_pair"}


@pytest.mark.parametrize("output", ["", "unexpected text", "Error: truncated", "configure pon interface "])
def test_invalid_source_is_not_confirmed_absence(output):
    with pytest.raises(UnknownIdentity):
        enumerate_children("card", "lt:1/1/2", "pon", output)


def test_table_requires_recognized_header_and_matching_footer_count():
    for output in ("", "garbled response", ont_table(ONT) + "\ninterface count : 2", "\n".join(ont_table(ONT).splitlines()[:-1])):
        with pytest.raises(UnknownIdentity):
            parse_ont_serials(output, PON)


def test_invalid_relation_is_rejected_even_with_no_children():
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.discovery import adapter_for
    with pytest.raises(UnknownIdentity):
        adapter_for("ont", "pon")
    with pytest.raises(UnknownIdentity):
        enumerate_children("ont", ONT, "pon", "#----------------")
    with pytest.raises(UnknownIdentity):
        result("ont", ONT, "pon", "ok", command="info configure pon interface flat", read_scope="family")


def test_equipment_hierarchy_uses_explicit_ids_and_implicit_rack_from_shelf():
    output = ("configure equipment shelf 2/3 planned-type nfxs-b\n"
              "configure equipment slot nt-a planned-type nant-e\n"
              "configure equipment applique ntio-1 planned-type ncnc-d\n"
              "configure equipment slot lt:2/3/5 planned-type fglt-b\n"
              "configure equipment slot vlt:2/3/63 unlock\n"
              "configure equipment ont interface 2/3/5/1/1 admin-state down\n")
    assert enumerate_children("msan", "", "rack", output)["children"] == ["2"]
    assert enumerate_children("rack", "2", "shelf", output)["children"] == ["2/3"]
    assert enumerate_children("msan", "", "card", output)["children"] == ["nt-a"]
    assert enumerate_children("msan", "", "applique", output)["children"] == ["ntio-1"]
    assert enumerate_children("shelf", "2/3", "card", output)["children"] == ["lt:2/3/5", "vlt:2/3/63"]
    assert enumerate_children("rack", "1", "shelf", output)["children"] == []


def test_bonding_and_lag_sources_do_not_confuse_underlying_ports():
    output = ("configure interface port bonding:1/1/3/1 user test\n"
              "configure interface port xdsl-line:1/1/3/1 admin-up\n"
              "configure interface port bonding:1/1/4/1 admin-up\n")
    assert enumerate_children("card", "lt:1/1/3", "bonding_group", output)["children"] == ["1/1/3/1"]
    output = "configure link-agg group 1/1/8/1 port 1/1/8/2\nconfigure link-agg port 1/1/8/2 passive-lacp\n"
    assert enumerate_children("card", "lt:1/1/8", "lag", output)["children"] == ["1/1/8/1"]


def test_successful_reenumeration_retires_only_the_current_relation_edges():
    g = graph()
    snapshot = json.loads(json.dumps(g))
    g = attach_discovery(g, [parse_ont_serials(ont_table(), PON)])
    assert g != snapshot
    manifest = coverage(g, "pon", PON)
    assert manifest["complete"] is True
    assert node_key("ont", ONT) not in manifest["nodes"]
    # The detached data is not destroyed, nor are other scopes' edges removed.
    assert node_key("ont", ONT) in {n["key"] for n in g["nodes"]}
    assert any(e["source"] == node_key("ont", ONT) for e in g["edges"])


def test_incremental_evidence_is_preserved_and_new_children_have_edges():
    g = build_graph({"pon_interfaces": [{"name": PON}]}, "M")
    g = attach_discovery(g, [parse_ont_serials(ont_table(ONT), PON)])
    g = attach_discovery(g, [parse_ont_slots(slot_config(SLOT), ONT)])
    assert len(g["discovery"]) == 2
    assert {"source": node_key("pon", PON), "relation": "contains", "target": node_key("ont", ONT)} in g["edges"]
    assert {"source": node_key("ont", ONT), "relation": "contains", "target": node_key("ont_slot", SLOT)} in g["edges"]
    manifest = coverage(g, "pon", PON)
    assert node_key("ont_slot", SLOT) in manifest["nodes"]
    assert any(m["parent"] == node_key("ont_slot", SLOT) for m in manifest["missing"])


def test_unordered_batch_handles_children_discovered_in_the_same_batch():
    g = build_graph({"pon_interfaces": [{"name": PON}]}, "M")
    g = attach_discovery(g, [parse_ont_slots(slot_config(SLOT), ONT), parse_ont_serials(ont_table(ONT), PON)])
    assert len(g["discovery"]) == 2


def test_stale_future_and_previous_job_evidence_never_certify_freshness():
    stamp = "2026-11-20T10:00:00Z"
    g = attach_discovery(graph(), [dict(parse_ont_serials(ont_table(), PON), collected_at=stamp)])
    assert coverage(g, "pon", PON, now="2026-11-20T10:01:00Z")["complete"] is True
    assert coverage(g, "pon", PON, now="2026-11-20T10:10:00Z")["complete"] is False
    assert coverage(g, "pon", PON, now="2026-11-20T09:00:00Z")["complete"] is False
    assert coverage(g, "pon", PON, now="2026-11-20T10:01:00Z", collected_since="2026-11-20T10:00:30Z")["complete"] is False


def test_discovery_record_cannot_fake_source_or_timestamp():
    item = parse_ont_serials(ont_table(), PON)
    for mutation in ({"command": "show something else"}, {"read_scope": "scoped"}, {"collected_at": "yesterday"},
                     {"collected_at": "2026-11-20T10:00:00"}, {"status": "maybe"}):
        with pytest.raises(ValueError):
            attach_discovery(graph(), [dict(item, **mutation)])


@pytest.mark.parametrize("output", ["configure equipment shelf", "configure equipment slot", "configure equipment applique"])
def test_incomplete_equipment_identity_cannot_confirm_absence(output):
    kind = output.split()[-1]
    child_kind = {"shelf": "shelf", "slot": "card", "applique": "applique"}[kind]
    parent_kind, identity = ("rack", "1") if child_kind == "shelf" else ("msan", "")
    with pytest.raises(UnknownIdentity):
        enumerate_children(parent_kind, identity, child_kind, output)


# --- Channel pairs, transceiver inventory and UNI VLAN ports -------------------

UNI = SLOT + "/1"


def transceiver_table(*identities):
    # Format live-verified on DS-LIN-TEST-01 (header, index column, footer).
    lines = [
        "====================================================================================================",
        "transceiver-inventory table",
        "====================================================================================================",
        "index                 |inventory-status  |nokia-part-num|tx-wavelength|fiber-type   |rssi-sfptype   ",
        "----------------------+------------------+--------------+-------------+-------------+---------------",
    ]
    for identity in identities:
        lines.append("%-22s cage-empty         not-available  not-available not-available not-available  " % identity)
    lines.append("----------------------------------------------------------------------------------------------------")
    lines.append("transceiver-inventory count : %d" % len(identities))
    lines.append("====================================================================================================")
    return "\n".join(lines)


def test_channel_pair_enumeration_filters_family_source_by_card():
    cfg = ("configure channel-pair profiles wavelength-prof 1 name x upstream-channel-id 1 downstream-channel-id 1\n"
           "configure channel-pair interface 1/1/9/1 label pair-one\n"
           "configure channel-pair interface 1/1/9/2 label pair-two\n"
           "configure channel-pair interface 1/1/10/1 label other-card\n")
    item = enumerate_children("card", "lt:1/1/9", "channel_pair", cfg)
    assert item["status"] == "ok" and item["read_scope"] == "family"
    assert item["children"] == ["1/1/9/1", "1/1/9/2"]
    assert item["command"] == "info configure channel-pair interface flat"


def test_transceiver_inventory_filters_by_card_and_applique():
    table = transceiver_table("lt:1/1/8:sfp:1", "lt:1/1/8:sfp:2", "lt:1/1/6:qsfp:1",
                              "nt-a:xfp:1", "nt-b:xfp:1", "ntio-1:sfp:6")
    item = enumerate_children("card", "lt:1/1/8", "transceiver", table)
    assert item["status"] == "ok" and item["read_scope"] == "device"
    assert item["children"] == ["lt:1/1/8:sfp:1", "lt:1/1/8:sfp:2"]
    assert enumerate_children("card", "nt-a", "transceiver", table)["children"] == ["nt-a:xfp:1"]
    assert enumerate_children("applique", "ntio-1", "transceiver", table)["children"] == ["ntio-1:sfp:6"]
    assert enumerate_children("card", "lt:1/1/2", "transceiver", table)["children"] == []


def test_empty_transceiver_inventory_confirms_absence():
    item = enumerate_children("card", "lt:1/1/8", "transceiver", transceiver_table())
    assert item["status"] == "ok" and item["children"] == []


@pytest.mark.parametrize("mutation", ["missing_footer", "wrong_count", "no_header", "undecodable_row"])
def test_transceiver_inventory_fail_closed(mutation):
    table = transceiver_table("lt:1/1/8:sfp:1")
    if mutation == "missing_footer":
        table = "\n".join(line for line in table.splitlines() if "count :" not in line)
    elif mutation == "wrong_count":
        table = table.replace("transceiver-inventory count : 1", "transceiver-inventory count : 2")
    elif mutation == "no_header":
        table = "garbled response"
    else:
        table = transceiver_table("lt:1/1/8:sfp:1", "nt:sfp:1")
    with pytest.raises(UnknownIdentity):
        enumerate_children("card", "lt:1/1/8", "transceiver", table)


def stack_table(*pairs):
    # Format live-verified on DS-LIN-TEST-01 (header, higher/lower columns,
    # "stack count : N" footer).
    lines = [
        "===============================================================================================",
        "stack table",
        "===============================================================================================",
        "higher                                         |lower                                          ",
        "-----------------------------------------------+-----------------------------------------------",
    ]
    for higher, lower in pairs:
        lines.append("%-47s %-47s" % (higher, lower))
    lines.append("-----------------------------------------------------------------------------------------------")
    lines.append("stack count : %d" % len(pairs))
    lines.append("===============================================================================================")
    return "\n".join(lines)


def edge_exists(g, source, relation, target):
    return {"source": node_key(*source), "relation": relation, "target": node_key(*target)} in g["edges"]


def test_bridge_port_enumeration_uses_the_typed_stack_lower_interface():
    table = stack_table(
        ("bridge-port:%s" % UNI, "uni:%s" % UNI),
        ("bridge-port:1/1/8/1", "la-group:1/1/8/1"),
        ("bridge-port:1/1/3/1", "ethernet-line:1/1/3/1"),
        ("vlan-port:%s:99" % UNI, "bridge-port:%s" % UNI),
        ("la-group:1/1/8/1", "ethernet-line:1/1/8/1"),
    )
    item = enumerate_children("uni", UNI, "bridge_port", table)
    assert item["status"] == "ok" and item["read_scope"] == "device"
    assert item["children"] == [("uni", UNI)]
    assert item["command"] == "show interface stack"
    assert enumerate_children("lag", "1/1/8/1", "bridge_port", table)["children"] == [("lag", "1/1/8/1")]
    # An xDSL line's bridge port stacks on its ethernet-line (EFM) facet.
    assert enumerate_children("xdsl_line", "1/1/3/1", "bridge_port", table)["children"] == [("xdsl_line", "1/1/3/1")]
    assert enumerate_children("ethernet_port", "1/1/8/1", "bridge_port", table)["children"] == []
    json.dumps(item)


def test_vlan_port_enumeration_filters_stack_by_bridge_port():
    table = stack_table(
        ("vlan-port:%s:99" % UNI, "bridge-port:%s" % UNI),
        ("vlan-port:%s:100" % UNI, "bridge-port:%s" % UNI),
        ("vlan-port:%s:stacked:100:200" % UNI, "bridge-port:%s" % UNI),
        ("vlan-port:1/1/8/1:20", "bridge-port:1/1/8/1"),
    )
    item = enumerate_children("bridge_port", "uni:%s" % UNI, "vlan_port", table)
    assert item["status"] == "ok" and item["read_scope"] == "device"
    assert item["children"] == [("uni", UNI, "100"), ("uni", UNI, "99"), ("uni", UNI, "stacked:100:200")]
    assert item["parent"] == node_key("bridge_port", ("uni", UNI))
    lag_item = enumerate_children("bridge_port", ("lag", "1/1/8/1"), "vlan_port", table)
    assert lag_item["children"] == [("lag", "1/1/8/1", "20")]


def test_empty_stack_confirms_absence_and_round_trips():
    empty = stack_table()
    assert enumerate_children("uni", UNI, "bridge_port", empty)["children"] == []
    assert enumerate_children("bridge_port", ("uni", UNI), "vlan_port", empty)["children"] == []
    g = build_graph({"equipment_onts": {"interfaces": [{"ont_idx": ONT}], "slots": [{"ont_slot_idx": SLOT}]},
                     "ethernet_onts": [{"uni_idx": UNI}], "pon_interfaces": [{"name": PON}]}, "M")
    table = stack_table(("bridge-port:%s" % UNI, "uni:%s" % UNI), ("vlan-port:%s:99" % UNI, "bridge-port:%s" % UNI))
    results = [enumerate_children("uni", UNI, "bridge_port", table),
               enumerate_children("bridge_port", ("uni", UNI), "vlan_port", table)]
    g = attach_discovery(g, [json.loads(json.dumps(r)) for r in results])
    assert edge_exists(g, ("uni", UNI), "contains", ("bridge_port", ("uni", UNI)))
    assert edge_exists(g, ("bridge_port", ("uni", UNI)), "contains", ("vlan_port", ("uni", UNI, "99")))


@pytest.mark.parametrize("mutation", ["missing_footer", "wrong_count", "no_header", "bridge_address_mismatch",
                                      "vlan_address_mismatch", "bad_vlan"])
def test_stack_source_fail_closed(mutation):
    if mutation == "missing_footer":
        table = "\n".join(l for l in stack_table(("bridge-port:%s" % UNI, "uni:%s" % UNI)).splitlines()
                          if "count :" not in l)
        relation = ("uni", UNI, "bridge_port")
    elif mutation == "wrong_count":
        table = stack_table(("bridge-port:%s" % UNI, "uni:%s" % UNI)).replace("stack count : 1", "stack count : 2")
        relation = ("uni", UNI, "bridge_port")
    elif mutation == "no_header":
        table = "garbled response"
        relation = ("uni", UNI, "bridge_port")
    elif mutation == "bridge_address_mismatch":
        table = stack_table(("bridge-port:1/1/8/2", "la-group:1/1/8/1"))
        relation = ("lag", "1/1/8/1", "bridge_port")
    elif mutation == "vlan_address_mismatch":
        table = stack_table(("vlan-port:1/1/8/2:99", "bridge-port:1/1/8/1"))
        relation = ("bridge_port", ("lag", "1/1/8/1"), "vlan_port")
    else:
        table = stack_table(("vlan-port:%s:4095" % UNI, "bridge-port:%s" % UNI))
        relation = ("bridge_port", ("uni", UNI), "vlan_port")
    with pytest.raises(UnknownIdentity):
        enumerate_children(*relation, table)


def test_bonding_groups_have_no_bridge_ports_and_vlan_ports_need_a_bridge_parent():
    # Live stack evidence: bonding lowers are no-interface; VLAN ports are not
    # direct children of the port any more.
    with pytest.raises(UnknownIdentity):
        enumerate_children("bonding_group", "1/1/3/1", "bridge_port", "")
    with pytest.raises(UnknownIdentity):
        enumerate_children("uni", UNI, "vlan_port", "")


def test_uni_subtree_coverage_includes_bridge_and_vlan_port_relations():
    g = build_graph({"equipment_onts": {"interfaces": [{"ont_idx": ONT}], "slots": [{"ont_slot_idx": SLOT}]},
                     "ethernet_onts": [{"uni_idx": UNI}], "pon_interfaces": [{"name": PON}]}, "M")
    g = attach_discovery(g, [
        parse_ont_serials(ont_table(ONT), PON),
        parse_ont_slots(slot_config(SLOT), ONT),
        enumerate_children("ont_slot", SLOT, "uni", "configure ethernet ont %s admin-state up" % UNI),
    ])
    manifest = coverage(g, "pon", PON)
    assert manifest["complete"] is False
    assert any(m["parent"] == node_key("uni", UNI) and m["child_kind"] == "bridge_port" for m in manifest["missing"])
    table = stack_table(("bridge-port:%s" % UNI, "uni:%s" % UNI), ("vlan-port:%s:99" % UNI, "bridge-port:%s" % UNI))
    g = attach_discovery(g, [enumerate_children("uni", UNI, "bridge_port", table),
                             enumerate_children("bridge_port", ("uni", UNI), "vlan_port", table)])
    manifest = coverage(g, "pon", PON)
    assert manifest["complete"] is True
    assert node_key("vlan_port", ("uni", UNI, "99")) in manifest["nodes"]


def test_coverage_flags_documented_only_adapters_without_blocking():
    g = build_graph({"isam_equipment": {"slots": [{"id": "lt:1/1/2"}]}}, "M")
    manifest = coverage(g, "card", "lt:1/1/2")
    # channel-pair is implemented but documented-only; it is flagged, and the
    # rest of the card relations are live-verified.
    doc = {(d["parent"], d["child_kind"]) for d in manifest["documented_only"]}
    assert (node_key("card", "lt:1/1/2"), "channel_pair") in doc
    assert all(d["child_kind"] == "channel_pair" for d in manifest["documented_only"])
    # The flag is informational: it does not by itself make coverage incomplete.
    assert manifest["complete"] is False  # still false because reads are missing
