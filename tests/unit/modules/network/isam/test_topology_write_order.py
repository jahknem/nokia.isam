"""Write order derived from containment, references and the object-defining family."""
import pytest

from ansible.errors import AnsibleFilterError
from ansible_collections.nokia.isam.plugins.filter.topology import FilterModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.targeted import TARGETED_GATHER
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology import export_catalog
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.write_order import (
    DEFINES, DEVICE_SETTINGS_FIRST, UnorderedWrite, write_steps)

ONT = "1/1/6/7/1"
UNI = ONT + "/1/1"


def ont_move():
    """The families of one ONT as a migration creates them (NOC change set shape)."""
    return {
        "qos_profiles": [{"profile_type": "scheduler-node", "name": "N", "shaper-profile": "name:S"},
                         {"profile_type": "shaper", "name": "S"}],
        "equipment_onts": {"interfaces": [{"ont_idx": ONT, "sernum": "ALCL:00000001"}], "slots": [{"ont_slot_idx": ONT + "/1"}]},
        "ethernet_onts": [{"uni_idx": UNI}],
        "interfaces": [{"name": "pon:1/1/6/7", "admin_up": True}, {"name": "uni:" + UNI}, {"name": "vlan-port:" + UNI + ":10"}],
        "qos_interfaces": [{"name": "ont:" + ONT, "scheduler_node": "name:N"},
                           {"name": UNI, "upstream_queue": [{"id": 4, "bandwidth_profile": "name:B"}]},
                           {"name": "vlan:" + UNI + ":10"}],
        "bridges": {"port": [{"port": UNI, "vlan_id": [{"id": "10"}]}]},
        "ntp_onts": [{"ont_id": ONT}],
        "ani_onts": [{"ont_idx": ONT}],
        "isam_dhcp_relay": [{"name": "vlan:" + UNI + ":10"}],
    }


def order(result):
    return [(step["resource"], step["kinds"]) for step in result["steps"]]


def test_an_ont_is_created_top_down_and_removed_in_the_exact_reverse():
    create = write_steps(ont_move())
    assert order(create) == [
        ("qos_profiles", ["definition"]),
        ("interfaces", ["pon"]),
        ("equipment_onts", ["ont"]), ("ani_onts", ["ont"]), ("ntp_onts", ["ont"]), ("qos_interfaces", ["ont"]),
        ("equipment_onts", ["ont_slot"]),
        ("ethernet_onts", ["uni"]), ("interfaces", ["uni"]), ("qos_interfaces", ["uni"]),
        ("bridges", ["bridge_port"]),
        ("interfaces", ["vlan_port"]), ("isam_dhcp_relay", ["vlan_port"]), ("qos_interfaces", ["vlan_port"]),
    ]
    assert create["exhaustive"] is False
    delete = write_steps(ont_move(), "delete")
    assert order(delete) == list(reversed(order(create)))
    # Every instance lands in exactly one step, in its canonical section.
    assert create["steps"][2]["config"] == {"interfaces": [{"ont_idx": ONT, "sernum": "ALCL:00000001"}]}
    assert create["steps"][6]["config"] == {"slots": [{"ont_slot_idx": ONT + "/1"}]}
    assert [step["config"] for step in create["steps"] if step["resource"] == "qos_interfaces"] == [
        [{"name": "ont:" + ONT, "scheduler_node": "name:N"}],
        [{"name": UNI, "upstream_queue": [{"id": 4, "bandwidth_profile": "name:B"}]}],
        [{"name": "vlan:" + UNI + ":10"}]]


def test_the_uni_upstream_bandwidth_exists_before_its_bridge_port_takes_a_vlan():
    # Live apply 2026-11-19: VLAN attach without the UNI's upstream bandwidth profile
    # fails (device error 277). The UNI sits above its bridge port: no special rule.
    steps = order(write_steps(ont_move()))
    assert steps.index(("qos_interfaces", ["uni"])) < steps.index(("bridges", ["bridge_port"]))
    # A VLAN port exists only once its bridge port joined the VLAN.
    assert steps.index(("bridges", ["bridge_port"])) < steps.index(("interfaces", ["vlan_port"]))


def test_the_family_creating_an_object_comes_first_and_goes_last():
    create, delete = order(write_steps(ont_move())), order(write_steps(ont_move(), "delete"))
    ont_steps = [step for step in create if step[1] == ["ont"]]
    assert ont_steps[0] == ("equipment_onts", ["ont"])
    assert [step for step in delete if step[1] == ["ont"]][-1] == ("equipment_onts", ["ont"])
    for kind, (resource, section) in DEFINES.items():
        assert section in TARGETED_GATHER[resource]
        assert any(b["resource"] == resource and b["section"] == section for b in export_catalog()["bindings"]), kind


def test_definitions_come_before_their_referrers_and_cycles_are_refused():
    steps = write_steps(ont_move())["steps"]
    assert [p["name"] for p in steps[0]["config"]] == ["S", "N"]
    assert [p["name"] for p in write_steps(ont_move(), "delete")["steps"][-1]["config"]] == ["N", "S"]
    cyclic = {"qos_profiles": [{"profile_type": "shaper", "name": "S", "queue_profile": "name:Q"},
                               {"profile_type": "queue", "name": "Q", "shaper_profile": "name:S"}]}
    with pytest.raises(UnorderedWrite, match="cycle"):
        write_steps(cyclic)


def test_vlans_are_written_before_any_port_joins_them_and_removed_after():
    families = {"bridges": {"port": [{"port": UNI, "vlan_id": [{"id": "10"}]}]}, "vlans": [{"id": "10", "name": "HSI"}]}
    assert order(write_steps(families)) == [("vlans", ["device_settings"]), ("bridges", ["bridge_port"])]
    assert order(write_steps(families, "delete")) == [("bridges", ["bridge_port"]), ("vlans", ["device_settings"])]
    for resource in DEVICE_SETTINGS_FIRST:
        assert export_catalog()["section_models"]["%s.config" % resource]["model"] == "device_settings"


def test_consecutive_units_of_one_family_are_one_module_call():
    result = write_steps({"equipment_onts": {"interfaces": [{"ont_idx": ONT}], "slots": [{"ont_slot_idx": ONT + "/1"}]}})
    assert order(result) == [("equipment_onts", ["ont", "ont_slot"])]
    assert result["steps"][0]["config"] == {"interfaces": [{"ont_idx": ONT}], "slots": [{"ont_slot_idx": ONT + "/1"}]}


@pytest.mark.parametrize("families, message", [
    ({"no_such_family": []}, "No write order known"),
    ({"qos_interfaces": [{"name": "1/1/1/1"}]}, "ambiguous"),
    ({"bridges": {"port": [{"port": UNI}], "ageing_time": 300}}, "outside its instance lists"),
    ({"isam_traps": {"managers": [{"ip": "x"}]}}, "No write order evidence"),
    ({"ethernet_onts": [{"admin_state": "up"}]}, "without its identity"),
    ({"equipment_onts": [{"ont_idx": ONT}]}, "not its canonical form"),
    ({"ethernet_onts": ["1/1/1/1/1/1/1"]}, "must be mappings"),
    ({}, "non-empty"),
])
def test_anything_the_catalog_cannot_place_is_refused(families, message):
    with pytest.raises(UnorderedWrite, match=message):
        write_steps(families)


def test_phase_and_filter():
    with pytest.raises(UnorderedWrite):
        write_steps(ont_move(), "merge")
    write = FilterModule().filters()["isam_write_steps"]
    assert write(ont_move())["steps"][0]["resource"] == "qos_profiles"
    with pytest.raises(AnsibleFilterError, match="No write order known"):
        write({"no_such_family": []})
