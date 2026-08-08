from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.interface_cages.interface_cages import (
    InterfaceCagesFacts,
)


def test_interface_cage_operational_mode_is_parsed():
    facts = InterfaceCagesFacts(None)
    lines = facts._flatten_config(
        "configure interface cage lt:1/1/2:cage:1 operational-mode gpon"
    )
    parsed = facts.argument_spec
    assert lines == [
        "configure interface cage lt:1/1/2:cage:1 operational-mode gpon"
    ]
    assert "operational_mode" in parsed["config"]["options"]
