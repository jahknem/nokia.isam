"""The dependency graph: which part of a family must be configured before which, and why."""
import pytest

from ansible.errors import AnsibleFilterError
from ansible_collections.nokia.isam.plugins.filter.topology import FilterModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology import export_catalog
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.dependencies import (
    UnorderedWrite, build, dependency_graph, to_mermaid)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.write_order import write_steps

from .test_topology_write_order import ONT, UNI, ont_move


def edges(graph, reason=None):
    return {(e["before"], e["after"]) for e in graph["edges"] if reason in (None, e["reason"])}


def test_nodes_are_family_parts_by_the_object_they_address():
    graph = dependency_graph(ont_move())
    roles = {node["id"]: node["role"] for node in graph["nodes"]}
    # One family, three parts: the interfaces family addresses the PON, the UNI and the VLAN port.
    assert {"interfaces.config:pon", "interfaces.config:uni", "interfaces.config:vlan_port"} <= set(roles)
    assert roles["equipment_onts.interfaces:ont"] == "creates"
    assert roles["bridges.port:bridge_port"] == "creates"
    # The device creates these entries itself with the ONT / with the VLAN joining the bridge port.
    assert roles["ntp_onts.config:ont"] == roles["ani_onts.config:ont"] == "created_with"
    assert roles["interfaces.config:vlan_port"] == roles["qos_interfaces.config:vlan_port"] == "created_with"
    # The UNI exists with its ONT slot: no part creates it, the device creates its entries.
    assert roles["qos_interfaces.config:uni"] == roles["ethernet_onts.config:uni"] == "created_with"
    assert roles["qos_interfaces.config:ont"] == "created_with"
    assert roles["qos_profiles.config:definition"] == "definition"
    assert not graph["unplaced"] and graph["exhaustive"] is False


def test_every_edge_has_its_reason():
    graph = dependency_graph(ont_move())
    # The creating command before everything else configuring the same object.
    assert edges(graph, "creates") == {("equipment_onts.interfaces:ont", after) for after in (
        "ani_onts.config:ont", "ntp_onts.config:ont", "qos_interfaces.config:ont")}
    # Removing the ONT, its slot or a bridge port removes everything below (live 2026-11-25).
    objects = export_catalog()["objects"]
    assert all(objects[kind]["removal"]["removes_children"] for kind in ("ont", "ont_slot", "bridge_port"))
    # Inside-out containment, entered through the creating part of the inner object.
    contains = edges(graph, "contains")
    assert ("pon_interfaces.config:pon", "equipment_onts.interfaces:ont") not in contains  # not in this change set
    assert ("interfaces.config:pon", "equipment_onts.interfaces:ont") in contains
    assert ("qos_interfaces.config:ont", "equipment_onts.slots:ont_slot") in contains
    assert ("equipment_onts.slots:ont_slot", "ethernet_onts.config:uni") in contains
    assert ("qos_interfaces.config:uni", "bridges.port:bridge_port") in contains
    assert ("bridges.port:bridge_port", "interfaces.config:vlan_port") in contains
    # Only the creating part of the slot is entered from the ONT; nothing skips a level.
    assert ("interfaces.config:pon", "equipment_onts.slots:ont_slot") not in contains
    # Profiles before whatever names them.
    assert edges(graph, "references") == {("qos_profiles.config:definition", "qos_interfaces.config:%s" % kind)
                                          for kind in ("ont", "uni", "vlan_port")}
    # Declared requirements carry their evidence (device error 277, live 2026-11-19).
    requires = {(e["before"], e["after"]): e["evidence"] for e in graph["edges"] if e["reason"] == "requires"}
    assert set(requires) == {
        ("qos_interfaces.config:uni", "bridges.port:bridge_port"),        # errors 277, 135, 125
        ("qos_interfaces.config:ont", "equipment_onts.slots:ont_slot"),   # ds-queue-sharing, errors 58/59
        ("qos_interfaces.config:ont", "qos_interfaces.config:vlan_port"),  # us-vlanport-queue, errors 117/119
        ("qos_interfaces.config:ont", "qos_interfaces.config:uni"),        # us-queue-sharing, error 81
    }
    assert "277" in requires[("qos_interfaces.config:uni", "bridges.port:bridge_port")]


def test_the_write_order_is_a_topological_order_of_the_graph():
    families = dict(ont_move(), vlans=[{"id": "10", "name": "HSI"}])
    graph = dependency_graph(families)
    position = {name: index for index, name in enumerate(graph["order"])}
    assert all(position[e["before"]] < position[e["after"]] for e in graph["edges"])
    assert ("vlans.config:device_settings", "bridges.port:bridge_port") in edges(graph, "requires")
    # write_steps is that order, merged into module calls; removal is its reverse.
    flat = [(step["resource"], kind) for step in write_steps(families)["steps"] for kind in step["kinds"]]
    assert flat == [(name.split(".", 1)[0], name.rsplit(":", 1)[1]) for name in graph["order"]]
    reverse = [(step["resource"], kind) for step in write_steps(families, "delete")["steps"] for kind in step["kinds"]]
    assert reverse == flat[::-1]


def test_a_dependency_cycle_is_refused_not_broken_arbitrarily():
    catalog = export_catalog()
    catalog["requires"].append({"resource": "qos_interfaces", "section": "config", "target_resource": "bridges",
                                "target_section": "port", "target_kind": None, "evidence": "test"})
    with pytest.raises(UnorderedWrite, match="cycle"):
        build(ont_move(), catalog)


def test_what_cannot_be_placed_is_listed_for_a_graph_and_refused_for_a_write():
    families = {"bridges": {"port": [{"port": "1/1/4/3"}, {"port": UNI}]}, "igmp": {"packages": [{"index": 1}]}}
    graph = dependency_graph(families)
    assert [node["id"] for node in graph["nodes"]] == ["bridges.port:bridge_port"]
    assert {(u["resource"], u["identity"]) for u in graph["unplaced"]} == {("bridges", "1/1/4/3"), ("igmp", None)}
    with pytest.raises(UnorderedWrite):
        write_steps(families)


def test_a_bare_port_address_is_placed_only_from_an_object_the_same_configuration_identifies():
    # Live-verified attachment rule (identity.bridge_owner): the line at that address owns the bridge port.
    families = {"bridges": {"port": [{"port": "1/1/4/3"}]}, "interfaces": [{"name": "xdsl-line:1/1/4/3"}]}
    graph = dependency_graph(families)
    assert not graph["unplaced"]
    assert ("interfaces.config:xdsl_line", "bridges.port:bridge_port") in edges(graph, "contains")
    # QoS on a bare address is the line's where only the line is there ...
    families["qos_interfaces"] = [{"name": "1/1/4/3"}]
    graph = dependency_graph(families)
    assert not graph["unplaced"] and "qos_interfaces.config:xdsl_line" in [node["id"] for node in graph["nodes"]]
    # ... and not placed where a bonding group shares the address (owner not verified).
    families["interfaces"].append({"name": "bonding:1/1/4/3"})
    graph = dependency_graph(families)
    assert [u["resource"] for u in graph["unplaced"]] == ["qos_interfaces"]
    # ... and on an Ethernet card the LAG the device keeps at that index (QOS MGT error 216, live 2026-11-25).
    families = {"link_agg": {"groups": [{"id": "1/1/8/6"}], "ports": [{"id": "1/1/8/6"}]},
                "qos_interfaces": [{"name": "1/1/8/6"}]}
    graph = dependency_graph(families)
    assert not graph["unplaced"] and "qos_interfaces.config:lag" in [node["id"] for node in graph["nodes"]]


def test_mermaid_and_filter():
    graph = FilterModule().filters()["isam_dependency_graph"](ont_move())
    text = to_mermaid(graph)
    assert text.startswith("flowchart TD\n")
    assert 'subgraph ont["ont"]' in text and '"equipment_onts.interfaces (creates it)"' in text
    assert '"ntp_onts.config (created by the device)"' in text
    assert "  ont ==> ont_slot" in text and "-. requires .->" in text
    with pytest.raises(AnsibleFilterError):
        FilterModule().filters()["isam_dependency_graph"]({})

