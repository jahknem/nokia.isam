"""Regression tests: ethernet_line port-type-only lines and multi-attribute mau blocks."""
import pathlib

import pytest
from ansible.module_utils import basic

from ansible_collections.nokia.isam.tests.unit.modules.network.isam.isam_module import set_module_args
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.ethernet_line.ethernet_line import Ethernet_lineFacts
from . import lab_captures

CAPTURE = lab_captures.CONFIGURED


def parse(text):
    set_module_args({"state": "gathered", "config": None}, True)
    module = basic.AnsibleModule(argument_spec={"state": {"type": "str"}, "config": {"type": "list"}}, supports_check_mode=True)
    facts = {"ansible_network_resources": {}}
    Ethernet_lineFacts(module).populate_facts(None, facts, text)
    return facts["ansible_network_resources"]["ethernet_line"]


def test_port_type_only_line_does_not_crash():
    got = parse("configure ethernet line 1/1/8/1 port-type uni admin-up")
    assert got[0]["if_index"] == "1/1/8/1"
    assert got[0]["port_type"] == "uni"
    assert "mau" not in got[0]


def test_mau_block_keeps_type_and_power():
    got = parse("configure ethernet line 1/1/8/1 mau 1 type 1000basebx10d power up")
    mau = got[0]["mau"][0]
    assert mau["index"] == 1
    assert mau["mau_type"] == "1000basebx10d"
    assert mau["power"] == "up"


@pytest.mark.skipif(not CAPTURE.exists(), reason="lab capture not available")
def test_capture_ethernet_line_mau_power_present():
    lines = [l for l in CAPTURE.read_text().splitlines() if l.startswith("configure ethernet line ")]
    got = parse("\n".join(lines))
    with_mau = [e for e in got if e.get("mau")]
    assert with_mau
    assert any(m.get("power") for e in with_mau for m in e["mau"])
