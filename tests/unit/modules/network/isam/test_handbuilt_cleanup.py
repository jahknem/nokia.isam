"""Behaviour pinned while simplifying hand-built resource reconcilers."""
from copy import deepcopy

from .module_runner import run_module


def test_link_agg_merged_leaves_unrequested_fields_and_ports_alone(monkeypatch):
    running = (
        "configure link-agg port 1/1/6/1 passive-lacp actor-port-prio 123\n"
        "configure link-agg port 1/1/6/2 actor-port-prio 456\n"
        "configure link-agg group 1/1/6/1 priority 50 port 1/1/6/2\n"
    )
    config = {"ports": [{"id": "1/1/6/1", "short_timeout": True}],
              "groups": [{"id": "1/1/6/1", "ports": ["1/1/6/3"]}]}
    before = deepcopy(config)
    result = run_module(monkeypatch, "isam_link_agg", {"state": "merged", "config": config}, running)
    assert result["commands"] == [
        "configure link-agg port 1/1/6/1 short-timeout",
        "configure link-agg group 1/1/6/1 port 1/1/6/3"]
    assert config == before


def test_qos_maps_merged_does_not_modify_the_requested_entries(monkeypatch):
    running = "configure qos tc-map-dot1p 1 tc 2\n"
    config = {"tc_map_dot1p": [{"dot1p": 3, "tc": 4}]}
    before = deepcopy(config)
    result = run_module(monkeypatch, "isam_qos_maps", {"state": "merged", "config": config}, running)
    assert not result.get("failed"), result.get("msg")
    assert result["commands"] == ["configure qos tc-map-dot1p 3 tc 4"]
    assert config == before


def test_alarm_description_uses_shared_quoting(monkeypatch):
    result = run_module(monkeypatch, "isam_alarm", {"state": "rendered", "config": {
        "custom_profiles": [{"name": "zztest", "description1": '#test "quoted"'}]}})
    assert result["rendered"] == ['configure alarm custom-profile zztest description1 "#test \\"quoted\\""']
