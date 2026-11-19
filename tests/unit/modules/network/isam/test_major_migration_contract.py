"""Executable checks for the public migration examples, not the old API freeze."""
import json
from pathlib import Path

import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.equipment_onts.equipment_onts import Equipment_ontsArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.generic_pon.generic_pon import Generic_ponArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.vlans.vlans import VlansArgs

from .module_runner import run_module


@pytest.mark.parametrize("section,field,choices", [
    ("utilization", "pon_pmcollect", ["none", "pm-enable", "tca-enable"]),
    ("utilization", "ont_pmcollect", ["enable", "disable"]),
    ("ont", "slid_mode", ["ascii", "hexa-dec"]),
    ("ont", "sn_autounlock", ["enable", "disable"]),
    ("ont", "sw_ver_mis_block", ["enable", "disable"]),
    ("alarmflag", "ponlos_alarm_ctrl", ["enable", "disable"]),
])
def test_generic_pon_migration_choices_match_the_documented_contract(section, field, choices):
    spec = Generic_ponArgs.argument_spec["config"]["options"][section]["options"][field]
    assert spec["type"] == "str" and spec["choices"] == choices


VLAN_VALUE_OPTIONS = (
    "dhcp_opt82_nni", "dhcp_opt82_uplink", "relay_id_dhcp", "dhcp_linerate", "pppoe_linerate", "dhcpv6_linerate",
    "pppoe_l2_encaps", "dhcp_l2_encaps", "dhcpv6_l2_encaps", "l2_encaps1", "pppoer_vlanaware", "dhcpr_vlanaware",
    "dhcpv6r_vlanaware", "drly_srv_usr_side", "dhcpv6_relay_id", "dhcpv6_trst_port",
)


@pytest.mark.parametrize("field", VLAN_VALUE_OPTIONS)
def test_vlan_value_migration_retains_cli_spelling_as_an_input_alias(field):
    spec = VlansArgs.argument_spec["config"]["options"][field]
    assert spec["type"] == "str"
    assert field.replace("_", "-") in spec["aliases"]


def test_vlan_gathered_keys_are_canonical_but_cli_inputs_still_render(monkeypatch):
    running = "configure vlan id 3990 mode residential-bridge protocol-filter pass-pppoe drly-srv-usr-side enable\n"
    parsed = run_module(monkeypatch, "isam_vlans", {"state": "parsed", "running_config": running})["parsed"][0]
    assert parsed["protocol_filter"] == "pass-pppoe" and parsed["drly_srv_usr_side"] == "enable"
    assert "protocol-filter" not in parsed and "drly-srv-usr-side" not in parsed
    config = [{"id": "3990", "mode": "residential-bridge", "protocol-filter": "pass-pppoe", "drly-srv-usr-side": "enable"}]
    rendered = run_module(monkeypatch, "isam_vlans", {"state": "rendered", "config": config})["rendered"]
    assert "protocol-filter pass-pppoe" in "\n".join(rendered)
    assert "drly-srv-usr-side enable" in "\n".join(rendered)


@pytest.mark.parametrize("section", ["up_ctrl_pkt", "dn_ctrl_pkt"])
def test_old_queue_profile_maps_are_rejected_instead_of_silently_reinterpreted(monkeypatch, section):
    result = run_module(monkeypatch, "isam_qos_maps", {"state": "rendered", "config": {
        section: [{"protocol": "arp", "queue": 1, "profile": "example"}]}})
    assert result["failed"] and "Unsupported parameters" in result["msg"]
    assert not result.get("commands") and not result.get("rendered")


def test_documented_vp_link_list_renders_as_an_indexed_subnode(monkeypatch):
    config = {"vp_boards": [{"vp_board_id": "1/1/6", "vp_links": [{"link_id": "1", "lt_expect": "1/1/7"}]}]}
    result = run_module(monkeypatch, "isam_xdsl_boards", {"state": "rendered", "config": config})
    assert not result.get("failed"), result.get("msg")
    assert result["rendered"] == ["configure xdsl vp-board 1/1/6 vp-link 1 lt-expect 1/1/7"]


def test_bulk_facts_schema_allows_every_equipment_ont_section():
    schema_path = Path(__file__).resolve().parents[5] / "docs/schemas/isam_facts_resources.json"
    schema = json.loads(schema_path.read_text())
    sections = Equipment_ontsArgs.argument_spec["config"]["options"]
    declared = schema["properties"]["equipment_onts"]["properties"]
    assert set(sections) == set(declared)
    assert all(declared[section]["type"] == "array" and sections[section]["type"] == "list" for section in sections)
