from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ethernet_line import (
    Ethernet_lineTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_profiles import (
    Qos_profilesTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_profiles import (
    Xdsl_profilesTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.interface_cages.interface_cages import (
    InterfaceCagesFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.ethernet_line.ethernet_line import (
    Ethernet_lineFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.qos_interfaces.qos_interfaces import (
    Qos_interfacesFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.vlans.vlans import (
    VlansFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.xdsl_lines.xdsl_lines import (
    Xdsl_linesFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.iphost import (
    IphostTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.vlans import (
    VlansTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_lines import (
    Xdsl_linesTemplate,
)


def test_ethernet_line_template_accepts_compact_flat_line():
    parsed = Ethernet_lineTemplate(
        lines=["configure ethernet line 1/1/8/1 port-type uni"]
    ).parse()

    assert parsed == {"1/1/8/1": {"if_index": "1/1/8/1", "port_type": "uni"}}


def test_qos_profiles_template_accepts_compact_flat_line():
    parsed = Qos_profilesTemplate(
        lines=["configure qos profiles queue FD_BEQ red:24:48:80"]
    ).parse()

    assert parsed["queue:FD_BEQ"]["queue-type"] == "red:24:48:80"


def test_xdsl_profiles_template_accepts_packed_compact_flat_line():
    parsed = Xdsl_profilesTemplate().parse(
        "configure xdsl service-profile 1 name basic version 2 active"
    )

    assert parsed["service_profiles"] == [
        {"id": 1, "name": "basic", "version": 2, "active": True}
    ]


def test_xdsl_profiles_template_merges_compact_lines_for_one_profile():
    parsed = Xdsl_profilesTemplate().parse(
        "\n".join(
            [
                "configure xdsl service-profile 1 name basic",
                "configure xdsl service-profile 1 version 2",
            ]
        )
    )

    assert parsed["service_profiles"] == [{"id": 1, "name": "basic", "version": 2}]


def test_interface_cages_normalizes_compact_flat_lines_without_rewriting_them():
    facts = InterfaceCagesFacts(module=None)

    assert facts._flatten_config(
        "configure interface cage 1/1/1/1 description access"
    ) == ["configure interface cage 1/1/1/1 description access"]


def test_six_resources_normalize_live_compact_flat_lines():
    assert Ethernet_lineFacts(module=None)._compact_lines(
        ["configure ethernet line 1/1/8/1 port-type uni"],
        "configure ethernet line ",
    ) == ["configure ethernet line 1/1/8/1 port-type uni"]
    assert InterfaceCagesFacts(module=None)._flatten_config(
        "configure interface cage 1/1/1/1 description access apply-qos"
    ) == [
        "configure interface cage 1/1/1/1 description access",
        "configure interface cage 1/1/1/1 apply-qos",
    ]
    assert IphostTemplate(
        lines=["configure iphost name myhost"]
    ).parse() == {"name": "myhost"}
    assert Qos_interfacesFacts._compact_lines(
        ["configure qos interface 1/1/8/1 upstream-queue 0 bandwidth-profile name:qpsUP20Mbps"]
    ) == [
        "configure qos interface 1/1/8/1 upstream-queue 0 bandwidth-profile name:qpsUP20Mbps"
    ]
    assert VlansTemplate(lines=VlansFacts(module=None)._flatten_config(
        "configure vlan id 720 name VOICE-720 mode residential-bridge"
    )).parse() == {
        720: {"id": 720, "name": "VOICE-720", "mode": "residential-bridge"}
    }
    assert Xdsl_linesTemplate(lines=Xdsl_linesFacts(module=None)._flatten_config(
        "configure xdsl line 1/1/1/1 service-profile 11 spectrum-profile 101"
    )).parse() == {
        "1/1/1/1": {
            "name": "1/1/1/1",
            "service_profile": 11,
            "spectrum_profile": 101,
        }
    }
