"""Complete refresh of an ONT, PON or card: plan and evaluation (offline).

The contract: every applicable (object, section) and every referenced definition is
``present`` or ``absent`` (confirmed by the device), every child relation of every
known object has a fresh successful enumeration -- or the refresh is incomplete and
names the gap. A gap is never reported as "empty".
"""
from datetime import datetime, timedelta, timezone

import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.relations import FAMILIES
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology import discovery, refresh
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.identity import decode

ONT, SLOT, UNI = "1/1/7/16/1", "1/1/7/16/1/1", "1/1/7/16/1/1/1"
BRIDGE = ("uni", UNI)
NOW = datetime(2026, 11, 26, 12, 0, tzinfo=timezone.utc)


def at(seconds_ago=0):
    return (NOW - timedelta(seconds=seconds_ago)).isoformat().replace("+00:00", "Z")


def found(kind, identity, child_kind, children=(), seconds_ago=0):
    adapter = discovery.adapter_for(kind, child_kind)
    return discovery.result(kind, identity, child_kind, "ok", children=children, command=adapter["command"],
                            collected_at=at(seconds_ago), read_scope=adapter["read_scope"])


def ont_discovery(**kw):
    return [found("ont", ONT, "ont_slot", [SLOT], **kw), found("ont_slot", SLOT, "uni", [UNI], **kw),
            found("uni", UNI, "bridge_port", [BRIDGE], **kw), found("bridge_port", BRIDGE, "vlan_port", [], **kw)]


def answer(reads, absent=(), unverified=(), errors=(), data=None, dependency=None):
    """isam_read-shaped results: every id present unless named otherwise. ``dependency``
    maps (resource, section, id) to the dependency_gap label of an unverified id."""
    out = []
    for read in reads:
        result = dict(read, status="ok", returned_ids=[], confirmed_absent_ids=[], unverified_ids=[], data=[])
        if (read["resource"], read["section"]) in errors:
            result.update(status="error", error="read_failed")
            out.append(result)
            continue
        for value in read["ids"]:
            key = (read["resource"], read["section"], value if not isinstance(value, dict) else tuple(sorted(value.items())))
            gap = (dependency or {}).get(key)
            bucket = ("confirmed_absent_ids" if key in absent else "unverified_ids" if key in unverified or gap
                      else "returned_ids")
            result[bucket].append(value)
            if gap:
                result.setdefault("dependency_gaps", []).append({"id": value, "dependency_gap": gap})
        if data and (read["resource"], read["section"]) in data:
            result["data"] = data[(read["resource"], read["section"])]
        out.append(result)
    return out


def ctx(root, planned="fglt-b", nt=("nant-e", "nant-e")):
    """The context read of ``root`` answered like the lab: the card ``planned``, NT slots ``nt``."""
    read = refresh.context_reads(root)[0]
    rows = [{"id": slot, "planned_type": planned if slot.startswith("lt:") else nt[i - 1]}
            for i, slot in enumerate(read["ids"]) if slot.startswith("lt:") or nt[i - 1]]
    return [dict(read, status="ok", returned_ids=[r["id"] for r in rows], unverified_ids=[],
                 confirmed_absent_ids=[s for s in read["ids"] if s not in [r["id"] for r in rows]],
                 data={"slots": rows})]


def full_round(root, discoveries, absent=(), unverified=(), errors=(), data=None, context=None, dependency=None):
    context = ctx(root) if context is None else context
    objects = refresh.known_objects(root, discoveries)
    reads, _needs = refresh.configuration_reads(objects, refresh.context_from(context))
    results = context + answer(reads, absent, unverified, errors, data, dependency)
    while True:
        pending = refresh.pending_reference_reads(results)
        if not pending:
            break
        results += answer(pending)
    return refresh.evaluate(root, discoveries, results, now=NOW)


# -- encoders -------------------------------------------------------------------

def _samples():
    for kind, identity in refresh._SAMPLE.items():
        for resource, section, decoder in refresh.applicable_sections(kind):
            yield kind, identity, resource, section, decoder


@pytest.mark.parametrize("kind,identity,resource,section,decoder", list(_samples()),
                         ids=lambda v: v if isinstance(v, str) else None)
def test_every_encoder_is_the_inverse_of_its_decoder(kind, identity, resource, section, decoder):
    value = refresh.encode(decoder, kind, identity)
    known = {(kind, identity)} if not isinstance(identity, tuple) else {(identity[0], identity[1])}
    assert decode(decoder, value, known) == (kind, identity), (resource, section, value)


def test_ont_sections_come_from_the_relations():
    sections = {(r, s) for r, s, _d in refresh.applicable_sections("ont")}
    expected = {(r, s) for r, fam in FAMILIES.items() for s, spec in fam["sections"].items()
                if spec.get("object") == "ont"}
    assert expected <= sections
    assert {("interfaces", "config"), ("qos_interfaces", "config")} <= sections  # ont:<id> forms


def test_a_pon_qos_entry_is_addressed_with_its_prefix_and_a_uni_entry_bare():
    reads, _ = refresh.configuration_reads([("pon", "1/1/7/16"), ("uni", UNI)])
    qos = next(r for r in reads if r["resource"] == "qos_interfaces")
    assert qos["ids"] == sorted(["pon:1/1/7/16", UNI])


# -- ONT ------------------------------------------------------------------------

def test_ont_refresh_is_complete_when_every_section_is_present_or_confirmed_absent():
    root = ("ont", ONT)
    result = full_round(root, ont_discovery(), absent={("ntp_onts", "config", ONT)})
    assert result["complete"], result["gaps"]
    assert [k for k, _ in map(tuple, result["objects"])] == ["ont", "ont_slot", "uni", "bridge_port"]
    ntp = next(s for s in result["sections"] if s["resource"] == "ntp_onts")
    assert ntp["status"] == "absent"


def test_an_unverified_instance_is_a_named_gap_not_absence():
    # uni_onts entries are not created by the device with the UNI (unlike ani_onts with the ONT).
    result = full_round(("ont", ONT), ont_discovery(), unverified={("uni_onts", "config", UNI)})
    assert not result["complete"]
    assert {"kind": "uni", "identity": UNI, "resource": "uni_onts", "section": "config",
            "id": UNI, "status": "gap", "reason": "unverified"} in result["gaps"]


def test_a_failed_read_makes_every_addressed_object_a_gap():
    result = full_round(("ont", ONT), ont_discovery(), errors={("qos_interfaces", "config")})
    reasons = {(g["kind"], g["id"], g["reason"]) for g in result["gaps"] if g.get("resource") == "qos_interfaces"}
    assert reasons == {("ont", "ont:" + ONT, "read_read_failed"), ("uni", UNI, "read_read_failed")}


def test_a_section_never_read_is_a_gap():
    root = ("ont", ONT)
    reads, _ = refresh.configuration_reads(refresh.known_objects(root, ont_discovery()))
    results = ctx(root) + answer([r for r in reads if r["resource"] != "ethernet_onts"])
    result = refresh.evaluate(root, ont_discovery(), results, now=NOW)
    assert {"resource": "ethernet_onts", "reason": "not_read"}.items() <= next(
        g for g in result["gaps"] if g.get("resource") == "ethernet_onts").items()


def test_a_missing_discovery_relation_is_a_gap_and_its_subtree_unknown():
    discoveries = ont_discovery()[:1]  # slot found, its UNIs never enumerated
    result = full_round(("ont", ONT), discoveries)
    assert {"kind": "ont_slot", "identity": SLOT, "child_kind": "uni", "reason": "discovery_missing"} in result["gaps"]
    assert ["uni", UNI] not in result["objects"]


def test_a_failed_enumeration_is_never_an_empty_child_list():
    failed = discovery.result("ont", ONT, "ont_slot", "error", collected_at=at(), error="read_failed")
    result = full_round(("ont", ONT), [failed])
    assert result["objects"] == [["ont", ONT]]
    assert any(g.get("reason") == "discovery_error" for g in result["gaps"])


def test_stale_discovery_cannot_establish_children():
    result = full_round(("ont", ONT), ont_discovery(seconds_ago=600))
    assert result["objects"] == [["ont", ONT]]
    assert {"kind": "ont", "identity": ONT, "child_kind": "ont_slot", "reason": "discovery_stale"} in result["gaps"]


def test_referenced_profiles_are_read_and_their_absence_is_a_gap():
    root = ("ont", ONT)
    qos = [{"name": UNI, "cac_profile": "name:FD_ONTUniVideo", "scheduler_node": "name:NGLT_Default"}]
    objects = refresh.known_objects(root, ont_discovery())
    reads, _ = refresh.configuration_reads(objects)
    results = ctx(root) + answer(reads, data={("qos_interfaces", "config"): qos})
    profile_reads = refresh.reference_reads(results)
    assert profile_reads[0]["ids"] == [{"name": "FD_ONTUniVideo", "profile_type": "cac"},
                                       {"name": "NGLT_Default", "profile_type": "scheduler-node"}]
    missing = refresh.evaluate(root, ont_discovery(), results, now=NOW)
    assert not missing["complete"] and {g["reason"] for g in missing["gaps"]} == {"not_read"}
    done = refresh.evaluate(root, ont_discovery(), results + answer(profile_reads), now=NOW)
    assert done["complete"], done["gaps"]


# -- PON and card ---------------------------------------------------------------

def test_pon_refresh_walks_its_onts():
    root = ("pon", "1/1/7/16")
    discoveries = [found("pon", "1/1/7/16", "ont", [ONT])] + ont_discovery()
    result = full_round(root, discoveries)
    assert result["complete"], result["gaps"]
    assert ["uni", UNI] in result["objects"]


def test_pon_refresh_requests_its_discovery_rounds_in_order():
    root = ("pon", "1/1/7/16")
    first, _ = refresh.discovery_requests(root, [])
    assert [(r["kind"], r["child_kind"]) for r in first] == [("pon", "ont")]
    second, _ = refresh.discovery_requests(root, [found("pon", "1/1/7/16", "ont", [ONT])])
    assert [(r["kind"], r["child_kind"]) for r in second] == [("ont", "ont_slot")]


def test_card_refresh_names_relations_without_an_adapter():
    root = ("card", "lt:1/1/6")
    requests, unimplemented = refresh.discovery_requests(root, [])
    assert {r["child_kind"] for r in requests} >= {"pon", "xdsl_line", "ethernet_port", "cage", "lag"}
    result = refresh.evaluate(root, [], [], now=NOW)
    assert not result["complete"]
    assert {g["reason"] for g in result["gaps"]} >= {"discovery_missing"}
    assert all(g["reason"] == "discovery_unimplemented" for g in result["gaps"]
               if (g.get("kind"), g.get("child_kind")) in {(u["kind"], u["child_kind"]) for u in unimplemented})


def test_references_resolve_in_rounds_until_nothing_is_open():
    root = ("ont", ONT)
    qos = [{"name": UNI, "scheduler_node": "name:GPONShaperDN100Mbps"}]
    reads, _ = refresh.configuration_reads(refresh.known_objects(root, ont_discovery()))
    results = ctx(root) + answer(reads, data={("qos_interfaces", "config"): qos})
    first = refresh.pending_reference_reads(results)
    assert first[0]["ids"] == [{"name": "GPONShaperDN100Mbps", "profile_type": "scheduler-node"}]
    node = [{"profile_type": "scheduler-node", "name": "GPONShaperDN100Mbps", "shaper-profile": "name:GPONqssShaperDN100Mbps"}]
    results += [dict(r, data=node) for r in answer(first)]
    second = refresh.pending_reference_reads(results)
    assert second[0]["ids"] == [{"name": "GPONqssShaperDN100Mbps", "profile_type": "shaper"}]
    assert not refresh.evaluate(root, ont_discovery(), results, now=NOW)["complete"]  # the shaper is not read yet
    results += answer(second)
    assert refresh.pending_reference_reads(results) == []
    assert refresh.evaluate(root, ont_discovery(), results, now=NOW)["complete"]


def test_relay_and_pppoe_sections_apply_to_vlan_ports_only():
    for kind in ("pon", "ont", "uni"):
        resources = {r for r, _s, _d in refresh.applicable_sections(kind)}
        assert not resources & {"pppoe_client_interface", "pppoel2_statistics", "isam_arp_relay", "isam_dhcp_relay"}, kind
    vlan = {r for r, _s, _d in refresh.applicable_sections("vlan_port")}
    assert {"pppoe_client_interface", "pppoel2_statistics", "isam_arp_relay", "isam_dhcp_relay"} <= vlan


def test_configuration_shown_in_no_read_is_never_confirmed_absent():
    vlan = ("uni", UNI, "99")
    root = ("ont", ONT)
    discoveries = ont_discovery()[:3] + [found("bridge_port", BRIDGE, "vlan_port", [vlan])]
    result = full_round(root, discoveries, absent={("isam_dhcp_relay", "config", "vlan:%s:99" % UNI)})
    dhcp = next(s for s in result["sections"] if s["resource"] == "isam_dhcp_relay")
    assert dhcp["status"] == "gap" and dhcp["reason"] == "not_observable"
    arp = next(s for s in result["sections"] if s["resource"] == "isam_arp_relay")
    assert arp["status"] == "present"  # observable since the 2026-11-26 live check
    assert not result["complete"]


def test_an_entry_the_device_creates_with_its_object_and_shows_nothing_of_is_present_with_defaults():
    # equipment_onts loops/pm-collects exist with every ONT; flat prints nothing for defaults.
    result = full_round(("ont", ONT), ont_discovery(),
                        unverified={("equipment_onts", "loops", ONT), ("equipment_onts", "pm_collects", ONT)})
    loops = next(s for s in result["sections"] if s["section"] == "loops")
    assert loops["status"] == "present" and "reason" not in loops
    assert result["complete"], result["gaps"]


def test_a_failed_read_of_a_created_entry_stays_a_gap():
    result = full_round(("ont", ONT), ont_discovery(), errors={("equipment_onts", "loops")})
    loops = next(s for s in result["sections"] if s["section"] == "loops")
    assert loops["status"] == "gap"


def test_entries_created_with_a_missing_ont_are_absent_not_present():
    # Live DS-LIN-TEST-01 2026-11-27, free ONT index: 'equipment ont interface' says
    # "instance does not exist", 'interface port ont:<ont>' answers the header only.
    # The entry the device creates with the ONT cannot exist without it.
    root = ("ont", ONT)
    discoveries = [found("ont", ONT, "ont_slot", [])]
    absent = {("equipment_onts", "interfaces", ONT), ("equipment_onts", "loops", ONT),
              ("equipment_onts", "pm_collects", ONT), ("ani_onts", "config", ONT), ("ntp_onts", "config", ONT),
              ("qos_interfaces", "config", "ont:" + ONT), ("xdsl_onts", "config", ONT)}
    result = full_round(root, discoveries, absent=absent, unverified={("interfaces", "config", "ont:" + ONT)})
    port = next(s for s in result["sections"] if s["resource"] == "interfaces")
    assert port["status"] == "absent", port
    assert result["complete"], result["gaps"]


def test_an_entry_created_with_an_undecided_object_stays_a_gap():
    # The ONT's creating read failed: neither present nor absent can be concluded.
    root = ("ont", ONT)
    result = full_round(root, ont_discovery(), errors={("equipment_onts", "interfaces")},
                        unverified={("interfaces", "config", "ont:" + ONT)})
    port = next(s for s in result["sections"] if s["resource"] == "interfaces" and s["id"] == "ont:" + ONT)
    assert port["status"] == "gap" and port["reason"] == "unverified"


MISSING_ONT = {("equipment_onts", "interfaces", ONT), ("equipment_onts", "loops", ONT),
               ("equipment_onts", "pm_collects", ONT), ("ani_onts", "config", ONT), ("ntp_onts", "config", ONT),
               ("xdsl_onts", "config", ONT), ("interfaces", "config", "ont:" + ONT)}


def test_a_dependency_gap_under_a_missing_object_is_absent():
    # The QoS entry of a free ONT index: the device cannot resolve the interface
    # ("interface index cannot be calculated"); the ONT is proven absent by its
    # creating section, so the entry it would hang on is absent as well.
    result = full_round(("ont", ONT), [found("ont", ONT, "ont_slot", [])], absent=MISSING_ONT,
                        dependency={("qos_interfaces", "config", "ont:" + ONT): "interface-index"})
    qos = next(s for s in result["sections"] if s["resource"] == "qos_interfaces")
    assert qos["status"] == "absent" and "reason" not in qos, qos
    assert result["complete"], result["gaps"]


def test_a_dependency_gap_without_a_proven_missing_object_stays_a_labelled_gap():
    # The ONT exists (its slot was enumerated): a missing dependency proves nothing.
    result = full_round(("ont", ONT), ont_discovery(),
                        dependency={("bridges", "port", UNI): "lower-interface"})
    bridge = next(s for s in result["sections"] if s["resource"] == "bridges" and s["section"] == "port")
    assert bridge["status"] == "gap" and bridge["reason"] == "dependency_gap:lower-interface", bridge
    # The ONT's creating read failed: undecided, so the gap stays as well.
    result = full_round(("ont", ONT), [found("ont", ONT, "ont_slot", [])], errors={("equipment_onts", "interfaces")},
                        dependency={("qos_interfaces", "config", "ont:" + ONT): "interface-index"})
    qos = next(s for s in result["sections"] if s["resource"] == "qos_interfaces")
    assert qos["status"] == "gap" and qos["reason"] == "dependency_gap:interface-index", qos


def test_conflicting_existence_is_a_gap_never_absent_nor_present():
    # Fresh discovery shows the ONT's slot, UNI and bridge port, but the ONT's creating
    # section says "confirmed absent" (deleted within the freshness window, or two
    # sources that disagree): nothing below may be concluded from either side.
    result = full_round(("ont", ONT), ont_discovery(), absent={("equipment_onts", "interfaces", ONT)},
                        dependency={("bridges", "port", UNI): "lower-interface"})
    bridge = next(s for s in result["sections"] if s["resource"] == "bridges" and s["section"] == "port")
    assert bridge["status"] == "gap" and bridge["reason"] == "dependency_gap:lower-interface", bridge
    assert not result["complete"]
    # A PON refresh: the ONT is enumerated, its creating section says absent; the
    # entries created with it are neither present nor absent.
    root = ("pon", "1/1/7/16")
    discoveries = [found("pon", "1/1/7/16", "ont", [ONT]), found("ont", ONT, "ont_slot", [])]
    result = full_round(root, discoveries, absent={("equipment_onts", "interfaces", ONT)},
                        unverified={("ani_onts", "config", ONT), ("ntp_onts", "config", ONT), ("xdsl_onts", "config", ONT)})
    for resource in ("ani_onts", "ntp_onts", "xdsl_onts"):
        entry = next(s for s in result["sections"] if s["resource"] == resource)
        assert entry["status"] == "gap" and entry["reason"] == "conflicting_existence", entry
    assert {"kind": "ont", "identity": ONT, "reason": "conflicting_existence"} in result["gaps"]
    assert not result["complete"]


def test_a_failed_context_read_leaves_no_partial_context():
    good = ctx(("card", "lt:1/1/3"))
    failed = [dict(good[0], status="error", error="read_failed")]
    assert refresh.context_from(good + failed) == {"cards": {}, "nt": [], "read": False}
    assert refresh.context_from(good)["read"] is True


# -- card-type rules ---------------------------------------------------------------

DSL = ("card", "lt:1/1/3")


def lines(card, n, kind="xdsl_line"):
    return ["%s/%d" % (card[3:], i) for i in range(1, n + 1)]


def card_discovery(card, children, **kw):
    """Discoveries of a card's children plus empty bridge-port enumerations of its ports."""
    out = [found("card", card, kind, ids, **kw) for kind, ids in children.items()]
    for kind, ids in children.items():
        if kind in ("xdsl_line", "ethernet_port", "lag"):
            out += [found(kind, i, "bridge_port", [], **kw) for i in ids]
    return out


def test_a_card_of_a_known_type_enumerates_only_its_child_kinds():
    context = refresh.context_from(ctx(DSL, planned="ndlt-f"))
    requests, unimplemented = refresh.discovery_requests(DSL, [], context)
    assert {r["child_kind"] for r in requests} == {"xdsl_line", "bonding_group", "transceiver"}
    assert unimplemented == []  # uplink / ihub_port never apply to a line card
    na = refresh.not_applicable(*DSL, context)
    assert na["pon"] == na["ethernet_port"] == na["ihub_port"] == "card_type_not_applicable"


def test_card_sections_follow_the_card_type_and_the_system():
    def sections(planned, nt=("nant-e", "nant-e")):
        reads, _ = refresh.configuration_reads([DSL], refresh.context_from(ctx(DSL, planned=planned, nt=nt)))
        return {"%s.%s" % (r["resource"], r["section"]) for r in reads}
    assert sections("ndlt-f") == {"isam_equipment.slots", "qos_global.line_cards", "xdsl_boards.boards",
                                  "xdsl_bonding.boards"}
    assert sections("ndps-c") == {"isam_equipment.slots", "xdsl_boards.boards", "xdsl_boards.vp_boards"}
    assert sections("fglt-d") == {"isam_equipment.slots", "qos_global.line_cards"}
    # ipv6-antispoofing slot is refused for every board under NANT-E/NANT-A, shown under FANT-F.
    assert "isam_ipv6_antispoofing_slot.config" in sections("fglt-d", nt=("fant-f", None))


def test_a_card_entry_the_device_creates_with_the_card_is_present_with_defaults():
    children = {"xdsl_line": lines("lt:1/1/3", 48), "bonding_group": lines("lt:1/1/3", 48),
                "transceiver": ["lt:1/1/3:sfp:1"]}
    result = full_round(DSL, card_discovery("lt:1/1/3", children), context=ctx(DSL, planned="ndlt-f"),
                        unverified={("xdsl_bonding", "boards", "1/1/3"), ("qos_global", "line_cards", "lt:1/1/3")})
    bonding = next(s for s in result["sections"] if s["resource"] == "xdsl_bonding")
    assert bonding["status"] == "present" and "reason" not in bonding
    assert result["complete"], result["gaps"][:5]


def test_a_card_with_fewer_ports_than_its_type_has_is_incomplete():
    children = {"xdsl_line": lines("lt:1/1/3", 47), "bonding_group": lines("lt:1/1/3", 48),
                "transceiver": ["lt:1/1/3:sfp:1"]}
    result = full_round(DSL, card_discovery("lt:1/1/3", children), context=ctx(DSL, planned="ndlt-f"))
    assert {"kind": "card", "identity": "lt:1/1/3", "child_kind": "xdsl_line", "expected": 48, "found": 47,
            "reason": "population_mismatch"} in result["gaps"]


def test_an_unknown_or_unread_card_type_is_a_gap_and_nothing_is_excluded():
    unknown = refresh.context_from(ctx(DSL, planned="fwlt-c"))
    assert refresh.not_applicable(*DSL, unknown) == {"isam_ipv6_antispoofing_slot.config": "system_not_applicable"}
    requests, _ = refresh.discovery_requests(DSL, [], unknown)
    assert {"pon", "xdsl_line", "ethernet_port"} <= {r["child_kind"] for r in requests}
    assert refresh.context_gaps(DSL, unknown) == [{"kind": "card", "identity": "lt:1/1/3", "planned_type": "fwlt-c",
                                                   "reason": "card_type_unknown"}]
    result = refresh.evaluate(DSL, [], [], now=NOW)
    assert {"kind": "card", "identity": "lt:1/1/3", "reason": "card_type_not_read"} in result["gaps"]
    failed = [dict(ctx(DSL)[0], status="error", error="read_failed")]
    assert not refresh.context_from(failed)["read"]


def test_epon_is_never_read_on_a_gpon_card():
    root = ("pon", "1/1/7/16")
    result = full_round(root, [found("pon", "1/1/7/16", "ont", [])])
    assert result["complete"], result["gaps"]
    assert not any(s["resource"] == "epon_interfaces" for s in result["sections"])
    assert {"kind": "pon", "identity": "1/1/7/16", "name": "epon_interfaces.config",
            "reason": "card_type_not_applicable"} in result["not_applicable"]


def test_an_xdsl_line_is_also_read_under_its_ethernet_facet():
    reads, _ = refresh.configuration_reads([("xdsl_line", "1/1/3/1")])
    interfaces = next(r for r in reads if r["resource"] == "interfaces")
    assert interfaces["ids"] == ["ethernet-line:1/1/3/1", "xdsl-line:1/1/3/1"]
    assert interfaces["meta"]["objects"]["ethernet-line:1/1/3/1"] == [["xdsl_line", "1/1/3/1"]]


def test_a_vectoring_card_refresh_is_complete():
    root = ("card", "lt:1/1/1")
    sfps = ["lt:1/1/1:sfp:%d" % i for i in range(1, 5)]
    result = full_round(root, [found("card", "lt:1/1/1", "transceiver", sfps)], context=ctx(root, planned="ndps-c"))
    assert result["complete"], result["gaps"]
    assert {s["resource"] for s in result["sections"] if s["kind"] == "card"} == {"isam_equipment", "xdsl_boards"}
    # The vp-link SFPs have no diagnostics entry; SSM output never takes an LT port.
    assert not [s for s in result["sections"] if s["kind"] == "transceiver"]


def test_a_gpon_sfp_has_its_diagnostics_entry_with_defaults():
    root = ("card", "lt:1/1/5")
    pons = ["1/1/5/%d" % i for i in range(1, 17)]
    sfps = ["lt:1/1/5:sfp:%d" % i for i in range(1, 17)]
    cages = ["lt:1/1/5:cage:%d" % i for i in range(1, 17)]
    discoveries = card_discovery("lt:1/1/5", {"pon": pons, "cage": cages, "transceiver": sfps})
    discoveries += [found("pon", p, "ont", []) for p in pons]
    unverified = {("isam_equipment", "diagnostics_sfp", s) for s in sfps}
    result = full_round(root, discoveries, unverified=unverified)
    diag = [s for s in result["sections"] if s["section"] == "diagnostics_sfp"]
    assert len(diag) == 16 and {s["status"] for s in diag} == {"present"}
    assert result["complete"], result["gaps"][:5]
