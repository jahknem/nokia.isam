"""state: deleted against devices that actually have configuration.

The state contract only runs deleted against an empty device. Against a configured one
deleted crashed (PON variants), silently did nothing (an empty_fact_val dict of empty
lists is truthy), failed on a field without a removal form (interface cages), or --
with config naming one instance -- touched other sections and instances.
"""
import re

import pytest

from . import lab_captures
from .module_runner import lab_capture_device, module_for, run_module
from .test_resource_state_contract import RESOURCE_MODULES


@pytest.mark.parametrize("module_name,line,config,command", [
    ("isam_epon_interfaces", "configure epon interface 1/1/1/1 polling-period 10",
     [{"name": "1/1/1/1"}], "configure epon no interface 1/1/1/1"),
    ("isam_channel_pair_pm", "configure channel-pair interface 1/1/5/1 fec-tc-layer pm-collect enable",
     [{"name": "1/1/5/1"}], "configure channel-pair no interface 1/1/5/1"),
    ("isam_ngpon2_channel_groups", "configure channel-group id 1 polling-period 10",
     [{"id": 1}], "configure channel-group no id 1"),
])
def test_pon_variants_delete_existing_instances(monkeypatch, module_name, line, config, command):
    for args in ({"state": "deleted"}, {"state": "deleted", "config": config}):
        result = run_module(monkeypatch, module_name, args, line)
        assert not result.get("failed"), result.get("msg")
        assert result["commands"] == [command]


@pytest.mark.parametrize("module_name", ["isam_epon_interfaces", "isam_channel_pair_pm", "isam_ngpon2_channel_groups"])
def test_pon_variants_ignore_unrelated_lines(monkeypatch, module_name):
    text = "\n".join([
        "configure alarm log-full-action wrap",
        "configure equipment ont interface 1/1/5/1/3 sw-ver-pland auto",
        "configure system id name x",
    ])
    result = run_module(monkeypatch, module_name, {"state": "parsed", "running_config": text})
    assert not result.get("failed"), result.get("msg")
    assert not result["parsed"]


def test_xdsl_boards_deleted_without_config_removes_all(monkeypatch):
    text = "configure xdsl board 1/1/1 vce-profile 1\nconfigure xdsl board 1/1/3 vce-profile 2"
    for config in (None, {}, {"boards": [], "vp_boards": []}):
        args = {"state": "deleted"} if config is None else {"state": "deleted", "config": config}
        result = run_module(monkeypatch, "isam_xdsl_boards", args, text)
        assert not result.get("failed"), result.get("msg")
        assert result["commands"] == ["configure xdsl no board 1/1/1", "configure xdsl no board 1/1/3"]
    named = run_module(monkeypatch, "isam_xdsl_boards",
                       {"state": "deleted", "config": {"boards": [{"board_id": "1/1/3"}]}}, text)
    assert named["commands"] == ["configure xdsl no board 1/1/3"]


def test_mcast_general_deleted_resets_fast_change(monkeypatch):
    result = run_module(monkeypatch, "isam_mcast_general", {"state": "deleted"}, "configure mcast general fast-change")
    assert result["commands"] == ["configure mcast general no fast-change"]
    assert run_module(monkeypatch, "isam_mcast_general", {"state": "deleted"}, "")["commands"] == []


def test_interface_cages_keep_operational_mode_with_a_warning(monkeypatch):
    text = "configure interface cage lt:1/1/2:cage:1 operational-mode gpon"
    for args in ({"state": "deleted"}, {"state": "overridden", "config": [{"id": "lt:1/1/2:cage:2"}]}):
        result = run_module(monkeypatch, "isam_interface_cages", args, text)
        assert not result.get("failed"), result.get("msg")
        assert not any("operational-mode" in c for c in result["commands"])
        assert any("operational_mode" in w for w in result["_warnings"])


XDSL_PROFILES = "\n".join([
    "configure xdsl service-profile 15 name svc version 1 max-bitrate-down 110000",
    "configure xdsl service-profile 99 name zztest version 1",
    "configure xdsl spectrum-profile 1 name spec version 1",
    "configure xdsl dpbo-profile 4 name dpbo version 1",
    "configure xdsl vect-profile 10 name vect version 1",
])


def test_xdsl_profiles_deleting_one_profile_leaves_other_types_alone(monkeypatch):
    """Found by a dry run on the lab ISAM: it also deleted every spectrum/DPBO/vect profile."""
    result = run_module(monkeypatch, "isam_xdsl_profiles",
                        {"state": "deleted", "config": {"service_profiles": [{"id": 99}]}}, XDSL_PROFILES)
    assert result["commands"] == ["configure xdsl no service-profile 99"]
    absent = run_module(monkeypatch, "isam_xdsl_profiles",
                        {"state": "deleted", "config": {"service_profiles": [{"id": 98}]}}, XDSL_PROFILES)
    assert absent["commands"] == []
    everything = run_module(monkeypatch, "isam_xdsl_profiles", {"state": "deleted"}, XDSL_PROFILES)
    assert len(everything["commands"]) == 5


def test_equipment_deleting_one_applique_leaves_shelf_and_slots_planned(monkeypatch):
    text = "\n".join([
        "configure equipment shelf 1/1 planned-type nfxs-b",
        "configure equipment slot lt:1/1/5 planned-type fglt-b unlock",
        "configure equipment applique 1/1/7 planned-type nfpa-a",
    ])
    result = run_module(monkeypatch, "isam_equipment", {"state": "deleted", "config": {"appliques": [{"id": "1/1/7"}]}}, text)
    assert result["commands"] and all("applique 1/1/7" in c for c in result["commands"])


def test_xstp_deleting_a_port_does_not_disable_stp(monkeypatch):
    text = "configure xstp general enable-stp\nconfigure xstp port 1/1/3/1 priority 32"
    result = run_module(monkeypatch, "isam_xstp", {"state": "deleted", "config": {"ports": [{"port": "1/1/3/1"}]}}, text)
    assert result["commands"] == ["configure xstp port 1/1/3/1 no priority"]


def test_qos_maps_deleting_one_entry_by_identity(monkeypatch):
    text = "\n".join([
        "configure qos up-ctrl-pkt arp", "configure qos up-ctrl-pkt igmp",
        "configure qos dn-ctrl-pkt arp", "configure qos tc-map-dot1p 3 tc 2",
    ])
    up = run_module(monkeypatch, "isam_qos_maps", {"state": "deleted", "config": {"up_ctrl_pkt": [{"protocol": "arp"}]}}, text)
    assert up["commands"] == ["configure qos no up-ctrl-pkt arp"]
    tc = run_module(monkeypatch, "isam_qos_maps", {"state": "deleted", "config": {"tc_map_dot1p": [{"dot1p": 3}]}}, text)
    assert not tc.get("failed"), tc.get("msg")
    assert len(tc["commands"]) == 1 and "tc-map-dot1p 3" in tc["commands"][0]


# --- over the lab captures (skipped without them) ---

@pytest.mark.parametrize("module_name", RESOURCE_MODULES)
def test_deleted_without_config_never_fails_on_a_real_capture(monkeypatch, module_name):
    """No-ops are allowed (context selectors; isam_system by design); failures are not."""
    if not lab_captures.CONFIGURED.exists():
        pytest.skip("lab capture not available")
    result = run_module(monkeypatch, module_name, {"state": "deleted"}, lab_captures.CONFIGURED.read_text(errors="replace"))
    assert not result.get("failed"), "%s: deleted failed" % module_name  # no message: it may quote config


def _lab_instances(monkeypatch):
    """(module, list path, identity) for one instance of every targetable list on the lab device."""
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.targeted import TARGETED_GATHER

    flat = lab_captures.CONFIGURED.read_text(errors="replace")
    instances = []
    for resource, lists in sorted(TARGETED_GATHER.items()):
        name = module_for(resource)
        if name is None or name == "isam_system_security":  # identities can be secrets; own tests
            continue
        gathered = run_module(monkeypatch, name, {"state": "parsed", "running_config": flat}).get("parsed") or {}
        for path, ident in sorted(lists.items()):
            fields = ident if isinstance(ident, list) else [ident]
            node = gathered
            for part in ([] if path == "config" else path.split(".")):
                node = node.get(part) if isinstance(node, dict) else None
            entry = next((e for e in node or [] if all(e.get(f) is not None for f in fields)), None)
            if entry is not None:
                instances.append((name, path, dict((f, entry[f]) for f in fields)))
    return instances


def test_deleted_naming_one_instance_touches_only_it_on_the_lab_capture(monkeypatch):
    device = lab_capture_device()
    instances = _lab_instances(monkeypatch)
    assert len(instances) >= 30, len(instances)  # the lab device has ~50 targetable instances
    problems = []
    for name, path, key in instances:
        config = [key]
        if path != "config":
            for part in reversed(path.split(".")):
                config = {part: config}
        result = run_module(monkeypatch, name, {"state": "deleted", "config": config}, device)
        idents = [str(v) for v in key.values()]
        stray = [c for c in result["commands"]
                 if not all(re.search(r"(^|\s)" + re.escape(i) + r"(\s|$)", c) for i in idents)]
        if result.get("failed") or stray:
            problems.append("%s:%s" % (name, path))  # names only: commands may quote config
    assert not problems, problems
