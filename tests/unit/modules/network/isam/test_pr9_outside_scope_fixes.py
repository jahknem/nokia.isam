"""Regressions for bugs found by the PR #9 module review that sat outside the fix areas."""
import json

from .module_runner import run_module


def test_qos_maps_merged_entry_without_required_tc_fails_clearly(monkeypatch):
    # A new tc-map-dot1p entry without tc used to crash with KeyError: 'tc'.
    result = run_module(monkeypatch, "isam_qos_maps", {
        "state": "merged",
        "config": {"tc_map_dot1p": [{"dot1p": 3}]},
        "running_config": json.dumps({"tc_map_dot1p": [{"dot1p": 0, "tc": 0}]}),
    })
    assert result.get("failed"), result
    assert "tc" in result["msg"] and "KeyError" not in result["msg"], result["msg"]
    assert not result.get("commands"), result


def test_qos_maps_merged_entry_with_tc_renders(monkeypatch):
    result = run_module(monkeypatch, "isam_qos_maps", {
        "state": "merged",
        "config": {"tc_map_dot1p": [{"dot1p": 3, "tc": 2}]},
        "running_config": json.dumps({"tc_map_dot1p": [{"dot1p": 0, "tc": 0}]}),
    })
    assert not result.get("failed"), result
    assert "configure qos tc-map-dot1p 3 tc 2" in result["commands"], result["commands"]


def test_bridges_overridden_removes_unwanted_port_as_a_whole(monkeypatch):
    # Overridden used to fail with "parser bridge_port has no removal form".
    result = run_module(monkeypatch, "isam_bridges", {
        "state": "overridden",
        "config": {"port": [{"port": "1/1/1/1", "vlan_id": [{"id": 100}]}]},
        "running_config": json.dumps({"port": [
            {"port": "1/1/1/1", "vlan_id": [{"id": 100}]},
            {"port": "1/1/1/2", "vlan_id": [{"id": 200}]},
        ]}),
    })
    assert not result.get("failed"), result
    assert "configure bridge no port 1/1/1/2" in result["commands"], result["commands"]
    assert "configure bridge no port 1/1/1/1" not in result["commands"], result["commands"]
