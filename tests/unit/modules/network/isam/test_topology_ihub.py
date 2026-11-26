"""IHUB identities cannot be inferred from access-side interface-port syntax."""

from pathlib import Path

import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology import export_catalog
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.discovery import (
    attach_discovery, coverage, enumerate_children, evidence_for, SOURCES,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.graph import build_graph, node_key, plan_known_reads
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.identity import UnknownIdentity, decode, parent_of
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.ihub import optical_ports


def port_table():
    return (Path(__file__).parents[4] / "fixtures/ihub_ports/multisection/output.txt").read_text()


@pytest.mark.parametrize("identity,parent", [
    ("nt-a:xfp:3", ("card", "nt-a")),
    ("nt-b:xfp:1", ("card", "nt-b")),
    ("ntio-1:sfp:2", ("applique", "ntio-1")),
])
def test_ihub_optical_identity_is_distinct_from_transceiver(identity, parent):
    assert decode("uplink", identity) == ("uplink", identity)
    assert decode("transceiver", identity) == ("transceiver", identity)
    assert node_key("uplink", identity) != node_key("transceiver", identity)
    assert parent_of("uplink", identity) == parent
    # Rejecting the access-side identity is not evidence against IHUB identity.
    with pytest.raises(UnknownIdentity):
        decode("interface", identity)


@pytest.mark.parametrize("identity", ["nt:xfp:1", "nt-a:eth:1", "nt-a:AI:1", "lt:1/1/1", "nt-a:qsfp:1"])
def test_unverified_or_non_optical_forms_are_not_uplinks(identity):
    with pytest.raises(UnknownIdentity):
        decode("uplink", identity)


def test_optical_inventory_filters_internal_ports_not_down_ports():
    assert optical_ports(port_table()) == ["nt-a:xfp:1", "nt-a:xfp:2", "nt-b:xfp:1", "ntio-1:sfp:2"]
    item = enumerate_children("card", "nt-a", "uplink", port_table())
    assert item["children"] == ["nt-a:xfp:1", "nt-a:xfp:2"]
    assert item["command"] == "show port" and item["read_scope"] == "device"
    assert enumerate_children("applique", "ntio-1", "uplink", port_table())["children"] == ["ntio-1:sfp:2"]
    assert enumerate_children("card", "lt:1/1/1", "uplink", port_table())["children"] == []


def test_missing_owner_section_is_not_confirmed_absence():
    # No NTIO-2 section in this otherwise complete, recognized source.
    with pytest.raises(UnknownIdentity, match="no section for the requested owner"):
        enumerate_children("applique", "ntio-2", "uplink", port_table())


@pytest.mark.parametrize("mutate", [
    lambda s: "",
    lambda s: "unexpected reply",
    lambda s: "\n".join(s.splitlines()[:-1]),  # missing final delimiter
    lambda s: s.replace("Ports on NTIO-1", "Ports on UNKNOWN"),
    lambda s: s.replace("LAG/", "garbled"),
    lambda s: s.replace("Link Up", "NotKnown"),
    lambda s: s.replace("ntio-1:sfp:2", "ntio-1:qsfp:2"),
    lambda s: s.replace("nt-b:xfp:1", "nt-a:xfp:3"),  # wrong section
    lambda s: s.replace("nt-a:xfp:2", "nt-a:xfp:1"),  # duplicate row
    lambda s: s + "\nError: output truncated\n",
])
def test_bad_ihub_source_never_confirms_partial_or_empty_inventory(mutate):
    with pytest.raises(UnknownIdentity):
        # Includes failures on rows outside the requested parent.
        enumerate_children("card", "nt-a", "uplink", mutate(port_table()))


def test_optical_discovery_does_not_certify_ihub_configuration():
    graph = build_graph({"isam_equipment": {"slots": [{"id": "nt-a"}]}}, "M")
    graph = attach_discovery(graph, [enumerate_children("card", "nt-a", "uplink", port_table())])
    port = "nt-a:xfp:1"
    assert coverage(graph, "uplink", port)["complete"] is True  # physical leaf only
    plan = plan_known_reads(graph, "uplink", port)
    assert plan["complete"] is False and plan["executable"] is False
    assert plan["reads"] == []  # no fabricated access-side read commands
    assert {"node": node_key("uplink", port), "reason": "configuration_coverage_partial"} in plan["gaps"]
    assert not any(node["kind"] == "bridge_port" for node in graph["nodes"])
    assert export_catalog()["objects"]["uplink"]["configuration_status"] == "partial"
    assert export_catalog()["partial_configuration_domains"] == ["ihub_ports", "ihub_lags", "ihub_services"]


def test_new_source_does_not_acquire_live_verified_provenance(monkeypatch):
    monkeypatch.setitem(SOURCES, "future_child", {"parents": ("card",)})
    assert evidence_for("card", "future_child") == "documented"


def test_full_msan_plan_exposes_ihub_domains_even_before_port_discovery():
    plan = plan_known_reads(build_graph({}, "M"), "msan", "")
    assert {gap["domain"] for gap in plan["gaps"] if gap["reason"] == "configuration_domain_unmodeled"} == {
        "ihub_router", "ihub_qos", "ihub_system_security", "ihub_other_domains",
    }
    assert plan["complete"] is False and plan["executable"] is False
