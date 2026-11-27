"""IHUB configuration sources must not be confused with the access flat root."""
import json
from pathlib import Path

import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.ihub_config import parse_ihub_config
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology import export_catalog
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.graph import build_graph, node_key, plan_known_reads


def config():
    return (Path(__file__).parents[4] / "fixtures/ihub_configuration/observed-shapes/output.txt").read_text()


def test_standalone_service_source_equals_root_projection():
    lines = config().splitlines()
    start = lines.index("    service")
    standalone = "----------------------------------------------\n" + "\n".join(lines[start + 1:-2]) + "\n----------------------------------------------"
    assert parse_ihub_config(standalone, "ihub_services")["config"] == parse_ihub_config(config(), "ihub_services")["config"]


@pytest.mark.parametrize("resource", ["ihub_ports", "ihub_lags", "ihub_services"])
@pytest.mark.parametrize("text", ["", "configure port nt-a:xfp:1 shutdown\n", "invalid token", 'echo "port-protection"\n----------'])
def test_unrecognized_source_never_confirms_empty_family(resource, text):
    with pytest.raises(ValueError):
        parse_ihub_config(text, resource)


@pytest.mark.parametrize("mutate", [
    lambda s: s.rsplit("\n", 2)[0],
    lambda s: s.replace("    exit\n----------------------------------------------", "----------------------------------------------"),
    lambda s: s.replace('description "LAB customer"', 'description "unterminated'),
    lambda s: s.replace("    lag 8", "    lag 7"),
])
def test_truncated_or_invalid_hierarchy_is_rejected(mutate):
    with pytest.raises(ValueError):
        parse_ihub_config(mutate(config()), "ihub_lags" if "lag 8" not in mutate(config()) else "ihub_services")


def test_unknown_configuration_is_partial_and_does_not_export_unknown_secret_values():
    text = config().replace('description "LAB customer"', 'description "LAB customer"\n            authentication-key SUPER_SECRET')
    parsed = parse_ihub_config(text, "ihub_services")
    assert parsed["coverage"]["complete"] is False
    assert parsed["coverage"]["unparsed"][0]["keyword"] == "authentication-key"
    assert "SUPER_SECRET" not in json.dumps(parsed)


@pytest.mark.parametrize("raw, value", [
    ("Bob's", "Bob's"),                          # unquoted apostrophe is literal, not shell quoting
    ('"Bob\'s uplink"', "Bob's uplink"),
    ("C:\\\\lab\\\\port", "C:\\\\lab\\\\port"),      # backslashes are kept, not consumed
    ('"a\\\\b c"', "a\\\\b c"),
])
def test_ihub_tokens_keep_apostrophes_and_backslashes(raw, value):
    text = config().replace('description "LAB optical port"', "description " + raw)
    ports = parse_ihub_config(text, "ihub_ports")
    assert ports["coverage"]["complete"]
    assert ports["config"][0]["description"] == value


def test_future_service_is_a_gap_not_a_silently_empty_complete_projection():
    text = config().replace("vpls 200 customer 10 v-vpls vlan 200 create", "vprn 200 customer 10 create")
    parsed = parse_ihub_config(text, "ihub_services")
    assert parsed["coverage"]["complete"] is False
    assert any(g["keyword"] == "vprn" for g in parsed["coverage"]["unparsed"])


def test_ihub_graph_binding_ownership_membership_and_references():
    resources = {name: parse_ihub_config(config(), name)["config"] for name in ("ihub_ports", "ihub_lags", "ihub_services")}
    graph = build_graph(resources, "M")
    assert graph["gaps"] == []
    edges = {(e["source"], e["relation"], e["target"]) for e in graph["edges"]}
    assert (node_key("uplink", "nt-a:xfp:1"), "member_of", node_key("ihub_lag", "7")) in edges
    assert (node_key("msan", ""), "owns", node_key("ihub_lag", "7")) in edges
    assert (node_key("msan", ""), "owns", node_key("ihub_virtual_port", "nt:vp:1")) in edges
    assert (node_key("card", "lt:1/1/7"), "contains", node_key("ihub_port", "lt:1/1/7")) in edges
    plan = plan_known_reads(graph, "ihub_service", ("vpls", "200"))
    assert {r["resource"] for r in plan["reads"]} == {"ihub_ports", "ihub_lags", "ihub_services"}
    assert all(r["section"] == "all" and r["ids"] == [] for r in plan["reads"])
    assert node_key("ihub_service", ("ies", "20")) not in plan["nodes"]  # no sibling consumers
    assert plan["complete"] is False and plan["executable"] is False
    assert any(g["reason"] == "configuration_coverage_partial" for g in plan["gaps"])
    assert not any(n["kind"] in ("lag", "bridge_port", "vlan_port") for n in graph["nodes"])


def test_ihub_capabilities_do_not_advertise_targeted_cli_reads():
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.targeted import TARGETED_GATHER
    catalog = export_catalog()
    for resource in ("ihub_ports", "ihub_lags", "ihub_services"):
        assert resource not in TARGETED_GATHER
        assert catalog["configuration_read_capabilities"][resource]["instance_selection"] == "whole_source_filter_only"
        assert resource in catalog["partial_configuration_domains"]


def test_ihub_zero_encapsulation_sap_references_a_port_not_access_vlan_zero():
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.ihub import sap_endpoint
    assert sap_endpoint("nt-a:xfp:4:0") == ("uplink", "nt-a:xfp:4")
    assert sap_endpoint("nt-a:eth:1:0") == ("ihub_port", "nt-a:eth:1")
    with pytest.raises(ValueError):
        sap_endpoint("nt-a:xfp:4:stacked:100:200")


def test_flat_root_facts_explicitly_report_known_ihub_omissions():
    # Config_treeFacts ships with the config-tree PR; until then this expectation skips.
    pytest.importorskip(
        "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.configuration.configuration")
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.configuration.configuration import Config_treeFacts

    class Module:
        params = {"config_tree_detail": True}

    class Conn:
        def get(self, command):
            assert command == "info configure detail flat"
            return "configure pon interface 1/1/5/1 admin-state up\n"

    facts = Config_treeFacts(Module()).populate_facts(Conn())
    assert facts["config_tree"]
    assert facts["config_tree_source"]["configuration_complete"] is False
    assert facts["config_tree_source"]["known_flat_source_omissions"] == ["ihub_ports", "ihub_lags", "ihub_services"]
