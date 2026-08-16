from pathlib import Path

import yaml

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.pon_variants import (
    Epon_interfacesTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.equipment_onts.equipment_onts import (
    Equipment_ontsFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.bridges.bridges import (
    BridgesFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.link_agg.link_agg import (
    Link_aggFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.interfaces.interfaces import (
    InterfacesFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.pon_interfaces.pon_interfaces import (
    Pon_interfacesFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.vlans.vlans import (
    VlansFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.interfaces import (
    InterfacesTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.link_agg import (
    Link_aggTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ani_onts import (
    Ani_ontsTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.pon_interfaces import (
    Pon_interfacesTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.software_mngt import (
    Software_mngtTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_profiles import (
    Qos_profilesTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.vlans import (
    VlansTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.voice_sip import (
    Isam_voice_sipTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_profiles import (
    Xdsl_profilesTemplate,
)


FIXTURE_ROOT = Path(__file__).parents[4] / "fixtures"
REQUIRED_DESCRIPTOR_FIELDS = {
    "schema_version",
    "resource",
    "device_type",
    "software_version",
    "command",
    "captured_at",
    "source",
}


def fixture_bundle(resource, name):
    bundle = FIXTURE_ROOT / resource / name
    with (bundle / "fixture.yml").open() as descriptor_file:
        descriptor = yaml.safe_load(descriptor_file)
    output = (bundle / "output.txt").read_text()
    return descriptor, output


def test_every_fixture_has_a_device_descriptor():
    descriptors = sorted(FIXTURE_ROOT.glob("*/**/fixture.yml"))
    assert descriptors
    for path in descriptors:
        with path.open() as descriptor_file:
            descriptor = yaml.safe_load(descriptor_file)
        assert REQUIRED_DESCRIPTOR_FIELDS <= set(descriptor)
        assert descriptor["schema_version"] == 1
        assert descriptor["device_type"]
        assert descriptor["software_version"]
        assert descriptor["source"] in {"sanitized-live-capture", "synthetic-regression"}
        assert path.with_name("output.txt").is_file()


def test_voice_fixture_is_parseable():
    descriptor, output = fixture_bundle("voice_sip", "r6.2.04m")
    parsed = Isam_voice_sipTemplate(lines=output.splitlines()).parse()
    assert descriptor["software_version"] == "R6.2.04m"
    assert any(entry["name"] == "vsp1" for entry in parsed["vsp"])


def test_software_fixture_is_parseable():
    descriptor, output = fixture_bundle("software_mngt", "r6.2.04m")
    parsed = Software_mngtTemplate(lines=output.splitlines()).parse()
    assert descriptor["device_type"] == "Nokia ISAM 7330 FTTN"
    assert len(parsed["oswp"]) == 2


def test_pon_variant_fixture_is_parseable():
    descriptor, output = fixture_bundle("pon_variants", "r6.2.04ng")
    parsed = Epon_interfacesTemplate(lines=output.splitlines()).parse()
    assert descriptor["command"] == "info configure epon interface flat"
    assert parsed["1/1/1/1"]["name"] == "1/1/1/1"


def test_bridge_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("bridges", "r6.2.04m")
    parsed = BridgesFacts(module=None)._parse_bridge_config(output)
    port = parsed["port"][0]
    vlans = {entry["id"]: entry for entry in port["vlan_id"]}

    assert descriptor["command"] == "info configure bridge flat"
    assert port["port"] == "1/1/2/1/1/1/1"
    assert port["pvid"] == 99
    assert vlans["20"]["l2fwder_vlan"] == 720
    assert vlans["20"]["qos"] == "priority:5"


def test_vlan_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("vlans", "r6.2.04m")
    facts = VlansFacts(module=None)
    parsed = VlansTemplate(lines=facts._flatten_config(output)).parse()

    assert descriptor["command"] == "info configure vlan id flat"
    assert parsed[99]["mode"] == "residential-bridge"
    assert parsed[99]["dhcp-opt82-ext"] == "add-or-forward"
    assert parsed[120]["priority"] == 5


def test_qos_profiles_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("qos_profiles", "r6.2.04m")
    parsed = Qos_profilesTemplate(lines=output.splitlines()).parse()

    assert descriptor["command"] == "info configure qos profiles flat"
    assert parsed["queue:FD_BEQ"]["queue-type"] == "red:24:48:80"
    assert parsed["scheduler-node:NGLT_Default"]["priority"] == 2
    assert parsed["policer:qpp5Mbps"]["committed-info-rate"] == 5120
    assert parsed["session:FD_Voice"]["up-policer"] == "name:FD_Pol_Voice"


def test_interfaces_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("interfaces", "r6.2.04m")
    raw_lines = [line.replace("configure interface ", "", 1) for line in output.splitlines()]
    parsed = InterfacesTemplate(lines=raw_lines).parse()
    parsed = {key: InterfacesFacts._canonicalize_entry(value) for key, value in parsed.items()}

    assert descriptor["command"] == "info configure interface port flat"
    assert parsed["uni:1/1/2/1/100/1/1"]["admin_up"] is True


def test_link_agg_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("link_agg", "r6.2.04m")
    facts = Link_aggFacts(module=None)
    parsed = list(Link_aggTemplate(lines=facts._flatten_config(output)).parse().values())
    ports = [item for item in parsed if item.get("type") == "port"]
    groups = [item for item in parsed if item.get("type") == "group"]

    assert descriptor["command"] == "info configure link-agg flat"
    assert ports[0]["passive_lacp"] is True
    assert groups[0]["load_sharing_policy"] == "mac-src"
    assert groups[0]["ports"]["1/1/8/1"] == "1/1/8/1"


def test_xdsl_profiles_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("xdsl_profiles", "r6.2.04m")
    template = Xdsl_profilesTemplate()
    parsed = template.normalize(template.parse(output))

    assert descriptor["command"] == "info configure xdsl *-profile flat"
    assert parsed["service_profiles"][0]["max_bitrate_down"] == 33000
    assert parsed["spectrum_profiles"][0]["dis_ansi_t1413"] is True
    assert parsed["dpbo_profiles"][0]["es_elect_length"] == 249
    assert parsed["vect_profiles"][0]["band_control_dn"] == "59:512"
    assert parsed["vce_profiles"][0]["vce_join_timeout"] == "auto"


def test_pon_interface_live_detail_fixture_is_parseable():
    descriptor, output = fixture_bundle("pon_interfaces", "r6.2.04m")
    facts = Pon_interfacesFacts(module=None)
    flattened = facts._flatten_config(output)
    parsed = Pon_interfacesTemplate(lines=flattened).parse()
    entry = parsed["1/1/2/1"]

    assert descriptor["command"] == "info configure pon interface flat detail"
    assert entry["admin_state"] == "up"
    assert entry["fec_dn"] == "disable"
    assert entry["tconts_per_frame"] == 64
    assert entry["tc_layer"]["pm_collect"] == "pm-enable"
    assert "pon_pmcollect" not in entry["utilization"]


def test_equipment_onts_live_detail_fixture_is_parseable():
    descriptor, output = fixture_bundle("equipment_onts", "r6.2.04m")
    parsed = Equipment_ontsFacts(module=None)._parse_config(output)

    assert descriptor["command"] == "info configure equipment ont flat detail"
    assert parsed["interfaces"][0]["ont_idx"] == "1/1/2/1/1"
    assert parsed["interfaces"][0]["sernum"] == "ALCL:SANITIZED"
    assert parsed["interfaces"][0]["enable_aes"] == "enable"
    assert parsed["slots"][0]["planned_card_type"] == "ethernet"
    assert parsed["slots"][0]["plndnumdataports"] == 1
    assert parsed["sw_ctrls"][0]["ont_variant"] == "DO"


def test_ani_fixture_is_parseable():
    descriptor, output = fixture_bundle("ani_onts", "r6.2.04m")
    parsed = Ani_ontsTemplate(lines=output.splitlines()).parse()
    assert descriptor["command"] == "info configure ani ont flat"
    assert parsed["1/1/2/1/1"]["tca_thresh"] is True


def test_ani_fixture_supports_the_observed_no_form():
    rendered = Ani_ontsTemplate().render(
        {"ont_idx": "1/1/2/1/1", "tca_thresh": False}, "tca_thresh"
    )
    assert rendered == "configure ani ont no tca-thresh 1/1/2/1/1"


def test_ani_threshold_fields_parse_and_render():
    parsed = Ani_ontsTemplate(
        lines=[
            "configure ani ont tca-thresh 1/1/2/1/1 lower-optical-th -25.5 upper-optical-th 0.5 rssi-profile 12",
        ]
    ).parse()

    assert parsed["1/1/2/1/1"]["lower_optical_th"] == -25.5
    assert parsed["1/1/2/1/1"]["upper_optical_th"] == 0.5
    assert parsed["1/1/2/1/1"]["rssi_profile"] == 12
    assert Ani_ontsTemplate().render(
        {"ont_idx": "1/1/2/1/1", "tca_thresh": True, "lower_optical_th": -25.5},
        "tca_thresh",
    ) == "configure ani ont tca-thresh 1/1/2/1/1 lower-optical-th -25.5"
