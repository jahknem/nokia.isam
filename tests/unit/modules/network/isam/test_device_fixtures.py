from pathlib import Path

import yaml

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.pon_variants import (
    Epon_interfacesTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.equipment_onts.equipment_onts import (
    Equipment_ontsFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.pon_interfaces.pon_interfaces import (
    Pon_interfacesFacts,
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.voice_sip import (
    Isam_voice_sipTemplate,
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
