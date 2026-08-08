from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.interface_cages.interface_cages import (
    InterfaceCagesFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.interface_cages import (
    InterfaceCagesTemplate,
)


def test_interface_cage_operational_mode_is_parsed():
    facts = InterfaceCagesFacts(None)
    lines = facts._flatten_config(
        "configure interface cage lt:1/1/2:cage:1 operational-mode gpon"
    )
    assert lines == [
        "configure interface cage lt:1/1/2:cage:1 operational-mode gpon"
    ]

    parsed = InterfaceCagesTemplate(lines=lines).parse()

    assert parsed == {
        "lt:1/1/2:cage:1": {
            "id": "lt:1/1/2:cage:1",
            "operational_mode": "gpon",
        }
    }


def test_interface_cage_operational_mode_is_parsed_from_hierarchical_output():
    facts = InterfaceCagesFacts(None)
    lines = facts._flatten_config(
        """configure interface
          cage lt:1/1/2:cage:1
            operational-mode xgs
          exit
        exit"""
    )

    parsed = InterfaceCagesTemplate(lines=lines).parse()

    assert parsed["lt:1/1/2:cage:1"]["operational_mode"] == "xgs"
