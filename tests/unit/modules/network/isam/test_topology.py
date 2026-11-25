"""Explicit object relationships and conservative recursive-read requirements."""
import json

import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology import export_catalog
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.objects import OBJECTS
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.graph import build_graph, node_key, plan_known_reads
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.identity import UnknownIdentity, decode
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.targeted import TARGETED_GATHER


ONT = "1/1/5/10/1"
UNI = ONT + "/2/1"


def sample():
    return {
        "equipment_onts": {"interfaces": [{"ont_idx": ONT, "log_auth_pwd": "not-exported"}],
                           "slots": [{"ont_slot_idx": ONT + "/2", "plndnumdataports": 1}]},
        "ethernet_onts": [{"uni_idx": UNI}],
        "interfaces": [{"name": "uni:" + UNI}, {"name": "vlan-port:" + UNI + ":99"}],
        "bridges": {"port": [{"port": UNI, "vlan_id": [{"id": 99}]}]},
        "qos_interfaces": [{"name": UNI, "queue": [{"queue_profile": "name:shared"}]}],
        "qos_profiles": [{"profile_type": "queue", "name": "shared", "shaper-profile": "name:limit"},
                         {"profile_type": "shaper", "name": "limit"}],
    }


def edge(graph, source, relation, target):
    return {"source": node_key(*source), "relation": relation, "target": node_key(*target)} in graph["edges"]


def test_catalog_reuses_targeted_identities_and_only_stores_direct_neighbors():
    catalog = export_catalog()
    assert "parents" not in OBJECTS["ont"]
    for binding in catalog["bindings"]:
        if binding["resource"] in TARGETED_GATHER:
            assert binding["identity"] == TARGETED_GATHER[binding["resource"]][binding["section"]]
        else:
            assert binding["read_scope"] == "all"
            assert binding["resource"] in catalog["configuration_read_capabilities"]
    assert catalog["objects"]["pon"]["children"] == ["ont"]
    assert catalog["objects"]["ont_slot"]["parents"] == ["ont"]
    assert "ont_slot" not in catalog["objects"]["pon"]["children"]
    catalog["objects"]["pon"]["children"].clear()
    assert export_catalog()["objects"]["pon"]["children"] == ["ont"]
    assert "equipment_onts.sw_ctrls" in export_catalog()["unmapped_sections"]
    json.dumps(export_catalog())


@pytest.mark.parametrize("decoder,value,expected", [
    ("card", "nt-a", ("card", "nt-a")),
    ("card", "vlt:1/1/63", ("card", "vlt:1/1/63")),
    ("lt_card", "1/1/6", ("card", "lt:1/1/6")),
    ("cage", "lt:1/1/5:cage:16", ("cage", "lt:1/1/5:cage:16")),
    ("interface", "ont:" + ONT, ("ont", ONT)),
    ("interface", "uni:" + UNI, ("uni", UNI)),
    ("interface", "xdsl-line:1/1/3/1", ("xdsl_line", "1/1/3/1")),
])
def test_explicit_identity_forms(decoder, value, expected):
    assert decode(decoder, value) == expected


@pytest.mark.parametrize("value", [ONT + "/1", ONT + "/1/1/1", "1/1/5/10/10", "ont:" + ONT])
def test_invalid_uni_is_never_matched_by_prefix(value):
    with pytest.raises(UnknownIdentity):
        decode("uni", value)


def test_graph_crosses_cli_branches_with_no_secret_payload_or_guessed_slots():
    graph = build_graph(sample(), "M")
    assert edge(graph, ("ont", ONT), "contains", ("ont_slot", ONT + "/2"))
    assert edge(graph, ("ont_slot", ONT + "/2"), "contains", ("uni", UNI))
    assert not any(n["kind"] == "ont_slot" and n["identity"] == ONT + "/1" for n in graph["nodes"])
    assert "not-exported" not in json.dumps(graph)
    assert graph["gaps"] == []


def test_scoped_plan_does_not_expand_to_sibling_ont_or_other_profile_consumers():
    data = sample()
    sibling = "1/1/5/10/10/1/1"
    data["qos_interfaces"].append({"name": sibling, "queue_profile": "name:shared"})
    graph = build_graph(data, "M")
    plan = plan_known_reads(graph, "ont", ONT)
    assert not plan["complete"] and not plan["executable"]
    assert any(g["reason"] == "discovery_missing" for g in plan["gaps"])
    assert node_key("uni", sibling) not in plan["nodes"]
    assert node_key("qos_profile", ("shaper", "limit")) in plan["nodes"]
    assert node_key("msan", "") not in plan["nodes"]
    assert all("scope" not in r for r in plan["reads"])
    assert all(sibling not in r["ids"] for r in plan["reads"])


def test_json_round_trip_and_deterministic_input_order():
    graph = build_graph(sample(), "M")
    reversed_graph = build_graph(dict(reversed(list(sample().items()))), "M")
    assert json.loads(json.dumps(graph)) == json.loads(json.dumps(reversed_graph))
    assert plan_known_reads(json.loads(json.dumps(graph)), "ont", ONT)["reads"] == plan_known_reads(graph, "ont", ONT)["reads"]


def test_dsl_ethernet_alias_uses_exact_typed_evidence_not_board_type():
    data = {"xdsl_lines": [{"name": "1/1/3/1"}], "interfaces": [{"name": "ethernet-line:1/1/3/1"}],
            "qos_interfaces": [{"name": "1/1/3/1"}]}
    graph = build_graph(data, "M")
    assert not graph["gaps"]
    assert edge(graph, ("card", "lt:1/1/3"), "contains", ("xdsl_line", "1/1/3/1"))
    assert not any(n["kind"] == "ethernet_port" for n in graph["nodes"])
    del data["xdsl_lines"]
    assert sum(g["reason"] == "unknown_owner" for g in build_graph(data, "M")["gaps"]) == 2


def test_explicit_interface_namespace_also_establishes_port_identity():
    data = {"interfaces": [{"name": "ethernet-line:1/1/3/1"}, {"name": "xdsl-line:1/1/3/1"}],
            "qos_interfaces": [{"name": "1/1/3/1"}]}
    graph = build_graph(data, "M")
    assert not graph["gaps"]
    assert edge(graph, ("card", "lt:1/1/3"), "contains", ("xdsl_line", "1/1/3/1"))


def test_controller_port_does_not_invent_a_shelf_or_make_linecards_its_children():
    graph = build_graph({"ethernet_line": [{"if_index": "nt-a:xfp:1"}],
                         "isam_equipment": {"slots": [{"id": "nt-a"}, {"id": "lt:1/1/5"}]}}, "M")
    assert edge(graph, ("msan", ""), "contains", ("card", "nt-a"))
    assert not any(n["kind"] == "uplink" for n in graph["nodes"])
    assert any(g["reason"] == "unknown_owner" for g in graph["gaps"])
    assert not edge(graph, ("card", "nt-a"), "contains", ("card", "lt:1/1/5"))


def test_missing_profiles_unknown_references_and_unmapped_resources_are_gaps():
    data = sample()
    data.pop("qos_profiles")
    data["qos_interfaces"][0]["future_knob"] = "name:future"
    data["equipment_onts"]["sw_ctrls"] = [{"sw_ctrl_id": 1}]
    data["epon_interfaces"] = [{"name": "unverified-id"}]
    data["new_family"] = {"thing": "value"}
    plan = plan_known_reads(build_graph(data, "M"), "ont", ONT)
    assert {g["reason"] for g in plan["gaps"]} >= {
        "unknown_reference", "referenced_definition_missing", "unmapped_resource", "unknown_owner"}


def test_unmapped_section_mechanism_still_reports_scope(monkeypatch):
    # Every current section is bound; the fail-closed mechanism must still work
    # for any future object-owned section awaiting a decoder.
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam import targeted
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology import scopes
    monkeypatch.setitem(targeted.TARGETED_GATHER["equipment_onts"], "future_list", "id")
    monkeypatch.setitem(scopes.OBJECT_OWNED_PENDING, "equipment_onts", ("future_list",))
    data = sample()
    data["equipment_onts"]["future_list"] = [{"id": "x"}]
    graph = build_graph(data, "M")
    gap = next(g for g in graph["gaps"] if g.get("section") == "future_list")
    assert gap["reason"] == "unmapped_section"
    assert gap["scope"] == "object_owned"


def test_global_settings_in_a_partly_mapped_family_are_not_silently_lost():
    data = sample()
    data["bridges"]["ageing_time"] = 300
    graph = build_graph(data, "M")
    assert not graph["gaps"]
    assert edge(graph, ("msan", ""), "owns", ("device_settings", "bridges"))
    # Newly introduced settings still require an explicit ownership declaration.
    data["bridges"]["future_global_setting"] = 1
    assert {"reason": "unmapped_settings", "resource": "bridges"} in build_graph(data, "M")["gaps"]


def test_ambiguous_service_identity_does_not_pick_the_first_matching_port_type():
    data = {"xdsl_lines": [{"name": "1/1/3/1"}], "ethernet_line": [{"if_index": "1/1/3/1"}],
            "qos_interfaces": [{"name": "1/1/3/1"}]}
    graph = build_graph(data, "M")
    gap = next(g for g in graph["gaps"] if g["resource"] == "qos_interfaces")
    assert gap["reason"] == "ambiguous_owner"
    assert {tuple(c) for c in gap["candidates"]} == {("xdsl_line", "1/1/3/1"), ("ethernet_port", "1/1/3/1")}
    config = node_key("configuration", ("qos_interfaces", "config", "1/1/3/1"))
    for owner in (("xdsl_line", "1/1/3/1"), ("ethernet_port", "1/1/3/1")):
        assert {"source": config, "relation": "candidate_owner", "target": node_key(*owner)} in graph["edges"]
    assert not any(e["relation"] == "configures" and e["source"] == config for e in graph["edges"])


def test_profile_cycles_terminate_and_never_walk_backwards():
    data = sample()
    data["qos_profiles"][1]["queue-profile"] = "name:shared"
    plan = plan_known_reads(build_graph(data, "M"), "ont", ONT)
    assert len([r for r in plan["reads"] if r["resource"] == "qos_profiles"]) == 1


def test_nested_vlan_includes_its_enclosing_read_unit_without_selecting_siblings():
    data = sample()
    data["bridges"]["port"][0]["vlan_id"].append({"id": 100})
    graph = build_graph(data, "M")
    plan = plan_known_reads(graph, "vlan_port", ("uni", UNI, "99"))
    assert {"resource": "bridges", "section": "port", "ids": [UNI]} in plan["reads"]
    assert node_key("vlan_port", ("uni", UNI, "100")) not in plan["nodes"]
    assert node_key("uni", UNI) not in plan["nodes"]


def test_bad_roots_versions_and_missing_identity_fail_closed():
    graph = build_graph({"ethernet_onts": [{"wrong_key": UNI}]}, "M")
    assert graph["gaps"][0]["reason"] == "missing_identity"
    with pytest.raises(ValueError):
        plan_known_reads(graph, "ont", ONT)
    graph["schema_version"] = 99
    with pytest.raises(ValueError):
        plan_known_reads(graph, "msan", "")


def test_ansible_filters_are_offline_and_preserve_blocked_coverage():
    from ansible.errors import AnsibleFilterError
    from ansible_collections.nokia.isam.plugins.filter.topology import FilterModule
    filters = FilterModule().filters()
    graph = filters["isam_topology"](sample(), "M")
    assert filters["isam_topology_read_requirements"](graph, "ont", ONT)["executable"] is False
    with pytest.raises(AnsibleFilterError):
        filters["isam_topology"]([], "M")
    with pytest.raises(AnsibleFilterError):
        filters["isam_topology_read_requirements"](None, "ont", ONT)


# --- Configuration scope classification ----------------------------------------

def test_every_targeted_section_has_an_explicit_scope():
    catalog = export_catalog()
    scopes = catalog["section_scopes"]
    for resource, sections in TARGETED_GATHER.items():
        for section in sections:
            assert "%s.%s" % (resource, section) in scopes
    assert catalog["unclassified_sections"] == []
    assert set(scopes.values()) <= {"object_owned", "device_global", "shared_profile"}
    expected = {"%s.%s" % (resource, section) for resource, sections in TARGETED_GATHER.items() for section in sections}
    expected |= {"%s.%s" % (b["resource"], b["section"]) for b in catalog["bindings"] if b["resource"] not in TARGETED_GATHER}
    assert set(catalog["section_models"]) == expected
    assert set(catalog["unbound_object_sections"]) == {key for key, value in catalog["section_models"].items()
                                                     if value["model"] == "unimplemented"}


def test_bound_sections_are_object_owned_and_global_sections_are_not_objects():
    catalog = export_catalog()
    scopes = catalog["section_scopes"]
    assert scopes["equipment_onts.interfaces"] == "object_owned"
    assert scopes["interfaces.config"] == "object_owned"
    assert scopes["system.sntp.servers"] == "device_global"
    assert scopes["isam_system_security.operators"] == "device_global"
    assert scopes["xdsl_profiles.service_profiles"] == "shared_profile"
    assert scopes["qos_profiles.config"] == "shared_profile"
    for key in ("qos_tca.config", "xstp.ports", "trouble_shooting_pon.interfaces", "isam_equipment.diagnostics_sfp",
                "isam_system_security.slots", "isam_system_security.pae.ports", "system.sync_if_timing.ssmout_synce"):
        assert scopes[key] == "object_owned"


def test_scope_conflict_is_a_catalog_error():
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology import scopes
    bindings = [{"resource": "system", "section": "sntp.servers"}]
    with pytest.raises(ValueError):
        scopes.section_scopes(bindings)


def test_security_slots_bind_nt_cards_and_undocumented_forms_stay_gaps():
    graph = build_graph({"isam_system_security": {"slots": [{"slot": "nt-a", "debug_usb": True}]}}, "M")
    assert not graph["gaps"]
    assert edge(graph, ("msan", ""), "contains", ("card", "nt-a"))
    assert any(n["kind"] == "configuration" and n["resource"] == "isam_system_security" for n in graph["nodes"])
    # Only nt-a/nt-b are documented; a bare LT slot form is not guessed.
    graph = build_graph({"isam_system_security": {"slots": [{"slot": "1/1/5"}]}}, "M")
    assert any(g["reason"] == "unknown_owner" and g.get("section") == "slots" for g in graph["gaps"])


def test_global_ownership_is_a_real_edge_and_carries_no_credential_identities():
    data = sample()
    data["dhcp_server"] = {"start_addr": "192.0.2.10"}
    data["isam_system_security"] = {"snmp_communities": [{"name": "sensitive-community-value"}],
                                    "operators": [{"name": "private-operator", "password": "private-password"}]}
    graph = build_graph(data, "M")
    assert edge(graph, ("msan", ""), "owns", ("device_settings", "dhcp_server"))
    assert edge(graph, ("msan", ""), "owns", ("device_settings", "isam_system_security"))
    serialized = json.dumps(graph)
    for value in ("sensitive-community-value", "private-operator", "private-password", "192.0.2.10"):
        assert value not in serialized
    ont_reads = plan_known_reads(graph, "ont", ONT)["reads"]
    assert not any(r["resource"] in ("dhcp_server", "isam_system_security") for r in ont_reads)
    msan_reads = plan_known_reads(graph, "msan", "")["reads"]
    assert {"resource": "dhcp_server", "section": "all", "ids": []} in msan_reads
    assert {"resource": "isam_system_security", "section": "all", "ids": []} in msan_reads


def test_xdsl_profiles_have_definition_and_reference_edges_without_other_consumers():
    data = {"xdsl_lines": [{"name": "1/1/3/1", "service_profile": "13", "spectrum_profile": "2"},
                           {"name": "1/1/3/2", "service_profile": "13"}],
            "xdsl_profiles": {"service_profiles": [{"id": "13"}], "spectrum_profiles": [{"id": "2"}]}}
    graph = build_graph(data, "M")
    assert not graph["gaps"]
    profile = ("shared_profile", ("xdsl_profiles", "service_profiles", "13"))
    assert edge(graph, ("msan", ""), "owns", profile)
    assert not edge(graph, ("msan", ""), "contains", profile)
    plan = plan_known_reads(graph, "xdsl_line", "1/1/3/1")
    assert node_key(*profile) in plan["nodes"]
    assert node_key("xdsl_line", "1/1/3/2") not in plan["nodes"]
    assert {"resource": "xdsl_profiles", "section": "service_profiles", "ids": ["13"]} in plan["reads"]
    data.pop("xdsl_profiles")
    plan = plan_known_reads(build_graph(data, "M"), "xdsl_line", "1/1/3/1")
    assert any(g["reason"] == "referenced_definition_missing" for g in plan["gaps"])


def test_queue_thresholds_and_pon_diagnostics_belong_to_their_objects():
    data = {"qos_tca": [{"name": UNI, "queue": 0}],
            "trouble_shooting_pon": {"interfaces": [{"name": "1/1/5/10"}]}}
    graph = build_graph(data, "M")
    assert not graph["gaps"]
    assert any(r["resource"] == "qos_tca" for r in plan_known_reads(graph, "ont", ONT)["reads"])
    assert any(r["resource"] == "trouble_shooting_pon" for r in plan_known_reads(graph, "pon", "1/1/5/10")["reads"])


def test_link_aggregation_members_are_associations_not_descendants():
    graph = build_graph({"link_agg": {"groups": [{"id": "1/1/8/1", "ports": ["1/1/8/1", "1/1/8/2"]}],
                                      "ports": [{"id": "1/1/8/1"}, {"id": "1/1/8/2"}]},
                         "interfaces": [{"name": "la-group:1/1/8/1"}]}, "M")
    assert not graph["gaps"]
    assert edge(graph, ("ethernet_port", "1/1/8/2"), "member_of", ("lag", "1/1/8/1"))
    assert not edge(graph, ("lag", "1/1/8/1"), "contains", ("ethernet_port", "1/1/8/2"))
    assert node_key("ethernet_port", "1/1/8/2") not in plan_known_reads(graph, "lag", "1/1/8/1")["nodes"]


def test_transceiver_diagnostics_stay_on_their_card():
    graph = build_graph({"isam_equipment": {"diagnostics_sfp": [{"id": "lt:1/1/6:qsfp:1"}]}}, "M")
    assert not graph["gaps"]
    assert edge(graph, ("card", "lt:1/1/6"), "contains", ("transceiver", "lt:1/1/6:qsfp:1"))
    plan = plan_known_reads(graph, "card", "lt:1/1/6")
    assert {"resource": "isam_equipment", "section": "diagnostics_sfp", "ids": ["lt:1/1/6:qsfp:1"]} in plan["reads"]


def test_global_timing_settings_do_not_hide_per_port_ssm_output():
    graph = build_graph({"system": {"sync_if_timing": {"revert": True,
                                                        "ssmout_synce": [{"port": "nt-a:xfp:1", "ssmout_enable": True}]}}}, "M")
    assert edge(graph, ("msan", ""), "owns", ("device_settings", "system"))
    assert edge(graph, ("card", "nt-a"), "contains", ("transceiver", "nt-a:xfp:1"))
    assert not any(g["reason"] == "unmapped_settings" for g in graph["gaps"])
    # The active-NT alias has no fixed physical owner; it stays an explicit gap.
    graph = build_graph({"system": {"sync_if_timing": {"ssmout_synce": [{"port": "nt:sfp:1"}]}}}, "M")
    assert any(g["reason"] == "unknown_owner" and g.get("section") == "sync_if_timing.ssmout_synce" for g in graph["gaps"])
    assert not any(g["reason"] == "unmapped_settings" for g in graph["gaps"])


# --- Evidence-backed bindings added while filling catalog gaps -----------------

def test_epon_and_channel_pair_configuration_bind_their_physical_ports():
    graph = build_graph({"epon_interfaces": [{"name": "1/1/2/1", "polling_period": 100}],
                         "channel_pair_pm": [{"name": "1/1/9/1", "fec_tc_layer": "enable"}]}, "M")
    assert not graph["gaps"]
    assert edge(graph, ("card", "lt:1/1/2"), "contains", ("pon", "1/1/2/1"))
    assert edge(graph, ("card", "lt:1/1/9"), "contains", ("channel_pair", "1/1/9/1"))
    plan = plan_known_reads(graph, "channel_pair", "1/1/9/1")
    assert {"resource": "channel_pair_pm", "section": "config", "ids": ["1/1/9/1"]} in plan["reads"]


def test_pppoe_sections_bind_vlan_ports_including_stacked_identities():
    uni = "1/1/5/1/3/1/1"
    graph = build_graph({
        "ethernet_onts": [{"uni_idx": uni}],
        "pppoe_client_interface": [{"name": "vlan-port:%s:99" % uni, "client_id": 1}],
        "pppoel2_statistics": [{"name": "vlan-port:%s:stacked:100:200" % uni, "enabled": True}],
    }, "M")
    assert not graph["gaps"]
    assert edge(graph, ("uni", uni), "contains", ("bridge_port", ("uni", uni)))
    assert edge(graph, ("bridge_port", ("uni", uni)), "contains", ("vlan_port", ("uni", uni, "99")))
    assert edge(graph, ("bridge_port", ("uni", uni)), "contains", ("vlan_port", ("uni", uni, "stacked:100:200")))
    plan = plan_known_reads(graph, "vlan_port", ("uni", uni, "stacked:100:200"))
    assert {"resource": "pppoel2_statistics", "section": "config", "ids": ["vlan-port:%s:stacked:100:200" % uni]} in plan["reads"]
    assert node_key("vlan_port", ("uni", uni, "99")) not in plan["nodes"]


def test_pppoe_atm_variant_identities_remain_explicit_gaps():
    graph = build_graph({"pppoe_client_interface": [{"name": "vlan-port:1/1/3/1:0:32:99", "client_id": 1}]}, "M")
    assert any(g["reason"] == "unknown_owner" and g["resource"] == "pppoe_client_interface" for g in graph["gaps"])


def test_pae_ports_bind_known_port_forms_and_leave_ont_service_forms_as_gaps():
    uni = "1/1/5/1/3/1/1"
    graph = build_graph({"isam_system_security": {"pae": {"ports": [
        {"port": uni, "authenticator": "enable"},
        {"port": "1/1/5/1/3/voip", "authenticator": "enable"},
    ]}}}, "M")
    assert any(n["kind"] == "uni" and n["identity"] == uni for n in graph["nodes"])
    assert any(n["kind"] == "configuration" and n["identity"] == uni for n in graph["nodes"])
    assert any(g["reason"] == "unknown_owner" and g.get("section") == "pae.ports" for g in graph["gaps"])


def test_bare_bridge_address_follows_the_verified_attachment_rule():
    # Live stack evidence: a bridge port at a LAG address stacks on the LAG;
    # at a DSL address it stacks on the line's EFM facet, never on bonding.
    data = {"ethernet_line": [{"if_index": "1/1/8/1"}],
            "link_agg": {"groups": [{"id": "1/1/8/1", "ports": ["1/1/8/1"]}]},
            "bridges": {"port": [{"port": "1/1/8/1", "vlan_id": [{"id": 99}]}]}}
    graph = build_graph(data, "M")
    assert not any(g["reason"] == "unknown_owner" and g["resource"] == "bridges" for g in graph["gaps"])
    assert edge(graph, ("lag", "1/1/8/1"), "contains", ("bridge_port", ("lag", "1/1/8/1")))
    assert edge(graph, ("bridge_port", ("lag", "1/1/8/1")), "contains", ("vlan_port", ("lag", "1/1/8/1", "99")))
    assert not edge(graph, ("ethernet_port", "1/1/8/1"), "contains", ("bridge_port", ("lag", "1/1/8/1")))
    # QoS bare names remain unresolved between the physical port and the LAG:
    # the stack table does not evidence the QoS session layer. The config stays
    # reachable from both candidates rather than being dropped.
    data["qos_interfaces"] = [{"name": "1/1/8/1"}]
    graph = build_graph(data, "M")
    gap = next(g for g in graph["gaps"] if g["resource"] == "qos_interfaces")
    assert gap["reason"] == "ambiguous_owner"
    assert {tuple(c) for c in gap["candidates"]} == {("ethernet_port", "1/1/8/1"), ("lag", "1/1/8/1")}
    # DSL: a QoS index is the physical port or la-group of a user port (device
    # help; only the bare form is accepted, live 2026-11-25), never a bonding
    # group. A bare QoS name at a bonded line address belongs to the line.
    data = {"xdsl_lines": [{"name": "1/1/3/1"}],
            "xdsl_bonding": {"groups": [{"group_id": "1/1/3/1"}]},
            "qos_interfaces": [{"name": "1/1/3/1"}]}
    graph = build_graph(data, "M")
    assert not [g for g in graph["gaps"] if g["resource"] == "qos_interfaces"]
    assert edge(graph, ("configuration", ("qos_interfaces", "config", "1/1/3/1")), "configures", ("xdsl_line", "1/1/3/1"))


@pytest.mark.parametrize("value,kind,parent", [
    ("nt-a:xfp:1", "card", "nt-a"),
    ("nt-b:qsfp:2", "card", "nt-b"),
    ("ntio-1:sfp:6", "applique", "ntio-1"),
    ("lt:1/1/8:sfp:36", "card", "lt:1/1/8"),
    ("lt:1/1/6:qsfp:1", "card", "lt:1/1/6"),
])
def test_transceiver_identity_forms_and_their_physical_owners(value, kind, parent):
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.identity import parent_of
    assert decode("transceiver", value) == ("transceiver", value)
    assert parent_of("transceiver", value) == (kind, parent)


@pytest.mark.parametrize("value", ["nt:sfp:1", "acu:1/1:1", "iont:1/1:1", "remote-sfp:1/1:sfp:1",
                                   "1/1/8/1", "lt:1/1/8:cfp2:1", "nt-a:xfp:0:1"])
def test_unmodelled_transceiver_forms_are_rejected(value):
    with pytest.raises(UnknownIdentity):
        decode("transceiver", value)


def test_stacked_vlan_port_identities_decode_and_round_trip():
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.identity import parent_of
    uni = "1/1/5/1/3/1/1"
    for name, vlan in (("vlan-port:%s:99" % uni, "99"), ("vlan-port:%s:stacked:100:200" % uni, "stacked:100:200")):
        assert decode("interface", name) == ("vlan_port", ("uni", uni, vlan))
        assert decode("vlan_port", ("uni", uni, vlan)) == ("vlan_port", ("uni", uni, vlan))
        assert parent_of("vlan_port", ("uni", uni, vlan)) == ("bridge_port", ("uni", uni))
        assert parent_of("bridge_port", ("uni", uni)) == ("uni", uni)
    for bad in ("vlan-port:%s:stacked:100" % uni, "vlan-port:%s:stacked:0:200" % uni, "vlan-port:%s:4095" % uni):
        with pytest.raises(UnknownIdentity):
            decode("interface", bad)


def test_bridges_stacked_vlan_association_creates_the_stacked_vlan_port():
    uni = "1/1/5/1/3/1/1"
    graph = build_graph({"ethernet_onts": [{"uni_idx": uni}],
                         "bridges": {"port": [{"port": uni, "vlan_id": [{"id": "stacked:100:200"}]}]}}, "M")
    assert not graph["gaps"]
    assert edge(graph, ("bridge_port", ("uni", uni)), "contains", ("vlan_port", ("uni", uni, "stacked:100:200")))


def test_pppoe_client_interface_references_its_ppp_profile_without_other_consumers():
    uni = "1/1/5/1/3/1/1"
    data = {"ethernet_onts": [{"uni_idx": uni}],
            "pppoe_client_interface": [{"name": "vlan-port:%s:99" % uni, "client_id": 1, "profile_name": "ppp-prof"},
                                       {"name": "vlan-port:%s:100" % uni, "client_id": 2, "profile_name": "ppp-prof"}],
            "pppoe_client_ppp_profile": [{"name": "ppp-prof"}]}
    graph = build_graph(data, "M")
    assert not graph["gaps"]
    profile = ("shared_profile", ("pppoe_client_ppp_profile", "config", "ppp-prof"))
    assert edge(graph, ("msan", ""), "owns", profile)
    plan = plan_known_reads(graph, "vlan_port", ("uni", uni, "99"))
    assert node_key(*profile) in plan["nodes"]
    assert node_key("vlan_port", ("uni", uni, "100")) not in plan["nodes"]
    assert {"resource": "pppoe_client_ppp_profile", "section": "config", "ids": ["ppp-prof"]} in plan["reads"]
    data.pop("pppoe_client_ppp_profile")
    plan = plan_known_reads(build_graph(data, "M"), "vlan_port", ("uni", uni, "99"))
    assert any(g["reason"] == "referenced_definition_missing" for g in plan["gaps"])


def test_xstp_ports_attach_to_the_port_object_not_a_bridge_port():
    # Live counterexample: xstp 1/1/8/6 is configured with a LAG present but
    # no bridge-port interface at that address (verified in the stack table).
    data = {"ethernet_line": [{"if_index": "1/1/8/6"}],
            "link_agg": {"groups": [{"id": "1/1/8/6", "ports": ["1/1/8/6"]}]},
            "xstp": {"ports": [{"port": "1/1/8/6", "path_cost": 200000}]}}
    graph = build_graph(data, "M")
    assert not graph["gaps"]
    assert not any(n["kind"] == "bridge_port" for n in graph["nodes"])
    plan = plan_known_reads(graph, "lag", "1/1/8/6")
    assert {"resource": "xstp", "section": "ports", "ids": ["1/1/8/6"]} in plan["reads"]


def test_ethernet_line_typed_name_is_the_line_facet_not_an_aggregate():
    data = {"xdsl_lines": [{"name": "1/1/3/1"}],
            "xdsl_bonding": {"groups": [{"group_id": "1/1/3/1"}]},
            "interfaces": [{"name": "ethernet-line:1/1/3/1"}, {"name": "bonding:1/1/3/1"}]}
    graph = build_graph(data, "M")
    assert not graph["gaps"]
    assert edge(graph, ("configuration", ("interfaces", "config", "ethernet-line:1/1/3/1")),
                "configures", ("xdsl_line", "1/1/3/1"))
    assert edge(graph, ("configuration", ("interfaces", "config", "bonding:1/1/3/1")),
                "configures", ("bonding_group", "1/1/3/1"))


def test_candidate_owned_qos_is_read_from_either_owner_without_selecting_the_other():
    data = {"ethernet_line": [{"if_index": "1/1/8/1"}],
            "link_agg": {"groups": [{"id": "1/1/8/1", "ports": ["1/1/8/1"]}]},
            "qos_interfaces": [{"name": "1/1/8/1", "cac_profile": "name:FD_Default"}],
            "qos_profiles": [{"profile_type": "cac", "name": "FD_Default"}]}
    graph = build_graph(data, "M")
    qos_config = node_key("configuration", ("qos_interfaces", "config", "1/1/8/1"))
    for kind in ("lag", "ethernet_port"):
        plan = plan_known_reads(graph, kind, "1/1/8/1")
        # The shared QoS read unit is included no matter which candidate is refreshed.
        assert {"resource": "qos_interfaces", "section": "config", "ids": ["1/1/8/1"]} in plan["reads"]
        assert qos_config in plan["nodes"]
        assert qos_config in plan["unresolved_ownership"]
        assert not plan["complete"] and not plan["executable"]
        # The other candidate object is NOT pulled into the subtree.
        other = "ethernet_port" if kind == "lag" else "lag"
        assert node_key(other, "1/1/8/1") not in plan["nodes"]
        # Its referenced profile definition is still resolved forwards.
        assert {"resource": "qos_profiles", "section": "config", "ids": [["cac", "FD_Default"]]} in plan["reads"]
    # A single canonical QoS object exists, not one per candidate.
    assert sum(1 for n in graph["nodes"] if n["kind"] == "configuration"
               and n["resource"] == "qos_interfaces" and n["identity"] == "1/1/8/1") == 1


def test_candidate_owners_helper_only_reports_bare_shared_addresses():
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.identity import candidate_owners
    known = {("xdsl_line", "1/1/3/1"), ("bonding_group", "1/1/3/1"), ("lag", "1/1/8/1")}
    assert candidate_owners("qos_interface", "1/1/3/1", known) == [("xdsl_line", "1/1/3/1")]
    assert candidate_owners("user_port", "1/1/3/1", known) == [("bonding_group", "1/1/3/1"), ("xdsl_line", "1/1/3/1")]
    assert candidate_owners("qos_interface", "1/1/8/1", known) == [("lag", "1/1/8/1")]
    assert candidate_owners("qos_interface", "1/1/5/1/3/1/1", known) == []
    assert candidate_owners("qos_interface", "vlan-port:1/1/3/1:99", known) == []
    assert candidate_owners("qos_tca", ("1/1/3/1", 0), known) == [("xdsl_line", "1/1/3/1")]


def test_discovery_evidence_separates_live_verified_from_documented():
    catalog = export_catalog()
    card = catalog["objects"]["card"]
    assert card["discovery"]["channel_pair"] == "implemented"
    assert card["discovery_evidence"]["channel_pair"] == "documented"
    assert card["discovery_evidence"]["transceiver"] == "live_verified"
    assert card["discovery_evidence"]["pon"] == "live_verified"
    assert catalog["objects"]["pon"]["discovery_evidence"]["ont"] == "live_verified"
    assert catalog["objects"]["uni"]["discovery_evidence"]["bridge_port"] == "live_verified"
    assert card["discovery_evidence"]["uplink"] == "live_verified"
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.discovery import evidence_for
    # Invalid/unimplemented relations carry no evidence claim.
    assert evidence_for("ont", "uplink") is None
    assert evidence_for("card", "channel_pair") == "documented"
    assert evidence_for("bridge_port", "vlan_port") == "live_verified"
