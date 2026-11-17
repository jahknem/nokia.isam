"""Regression: qos_maps ctrl-pkt real device form (dscp/pbit/tc) and dot1p-value render."""
import pathlib

import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_maps import Qos_mapsTemplate

CAPTURE = pathlib.Path("/path/to/pon-migration-planner/.local/root-flat.txt")


def test_bare_and_attributed_ctrl_pkt_parse():
    lines = [
        "configure qos up-ctrl-pkt arp",
        "configure qos up-ctrl-pkt igmp dscp 46 pbit 5 tc 7",
        "configure qos dn-ctrl-pkt dhcpv4 tc 3",
    ]
    got = Qos_mapsTemplate(lines=lines, module=None).parse()
    assert got["up_ctrl_pkt"][0] == {"protocol": "arp"}
    assert got["up_ctrl_pkt"][1] == {"protocol": "igmp", "dscp": 46, "pbit": 5, "tc": 7}
    assert got["dn_ctrl_pkt"][0] == {"protocol": "dhcpv4", "tc": 3}


def test_ctrl_pkt_render_round_trip():
    entry = {"protocol": "igmp", "dscp": 46, "pbit": 5, "tc": 7}
    cmd = Qos_mapsTemplate._render_up_ctrl_pkt(entry)
    assert cmd == "configure qos up-ctrl-pkt igmp dscp 46 pbit 5 tc 7"
    again = Qos_mapsTemplate(lines=[cmd], module=None).parse()
    assert again["up_ctrl_pkt"][0] == entry


def test_dscp_map_renders_dot1p_value():
    cmd = Qos_mapsTemplate._render_dscp_map_dot1p({"dscp": "0", "dot1p": 0})
    assert cmd == "configure qos dscp-map-dot1p 0 dot1p-value 0"


@pytest.mark.skipif(not CAPTURE.exists(), reason="lab capture not available")
def test_capture_ctrl_pkt_lines_all_parse():
    lines = [l for l in CAPTURE.read_text().splitlines()
             if l.startswith(("configure qos up-ctrl-pkt ", "configure qos dn-ctrl-pkt "))]
    got = Qos_mapsTemplate(lines=lines, module=None).parse()
    assert len(got["up_ctrl_pkt"]) + len(got["dn_ctrl_pkt"]) == len(lines)
