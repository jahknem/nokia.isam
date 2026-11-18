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


def test_qos_interface_deleted_skips_settings_that_are_not_configured(monkeypatch):
    """The device rejected 'no bc-scheduler-node' on an ONT UNI whose value was 'none'."""
    text = ("configure qos interface 1/1/7/16/1/1/1 scheduler-node name:NGLT_Default cac-profile name:FD_ONTUniVideo "
            "ds-num-rem-queue not-applicable mc-scheduler-node none bc-scheduler-node none")
    result = run_module(monkeypatch, "isam_qos_interfaces", {"state": "deleted", "config": [{"name": "1/1/7/16/1/1/1"}]}, text)
    assert not any("bc-scheduler-node" in c or "mc-scheduler-node" in c or "ds-num-rem-queue" in c
                   for c in result["commands"]), result["commands"]
    assert any("no scheduler-node" in c for c in result["commands"])


ONT_UNI_QOS = """configure qos interface 1/1/6/1/1/1/1 scheduler-node name:NGLT_Default cac-profile name:FD_ONTUniVideo ds-num-rem-queue not-applicable us-num-queue not-applicable oper-weight 50 oper-rate 0 mc-scheduler-node none bc-scheduler-node none
configure qos interface 1/1/6/1/1/1/1 queue 0 priority 6 weight 34 oper-weight 34 queue-profile name:NGLT_Default shaper-profile none
configure qos interface 1/1/6/1/1/1/1 upstream-queue 0 bandwidth-profile name:GPONqpp1000Mbps bandwidth-sharing uni-sharing
"""


def test_qos_interface_deleted_keeps_the_scheduler_node_of_an_interface_with_queues(monkeypatch):
    """Lab ISAM, ONT UNI: 'no scheduler-node' is refused while the interface has queues
    (QOS MGT error 52) and its queues cannot be removed; 'no us-num-queue' (error 48) and
    'no mc-/bc-scheduler-node' are refused for their 'not-applicable'/'none' values."""
    for config in ([{"name": "1/1/6/1/1/1/1"}], None):
        result = run_module(monkeypatch, "isam_qos_interfaces", {"state": "deleted", "config": config}, ONT_UNI_QOS)
        assert result["commands"] == [
            "configure qos interface 1/1/6/1/1/1/1 no cac-profile",
            "configure qos interface 1/1/6/1/1/1/1 upstream-queue 0 no bandwidth-profile",
            "configure qos interface 1/1/6/1/1/1/1 upstream-queue 0 no bandwidth-sharing",
        ], result["commands"]
        assert any("keeps scheduler-node name:NGLT_Default" in w for w in result["_warnings"]), result["_warnings"]


def test_qos_interface_deleted_removes_the_scheduler_node_of_an_ont(monkeypatch):
    """Accepted by the lab ISAM: an ont: QoS interface has no queues."""
    text = "configure qos interface ont:1/1/6/1/1 scheduler-node name:GPONShaperDN1000Mbps ds-num-queue not-applicable\n"
    result = run_module(monkeypatch, "isam_qos_interfaces", {"state": "deleted", "config": [{"name": "ont:1/1/6/1/1"}]}, text)
    assert result["commands"] == ["configure qos interface ont:1/1/6/1/1 no scheduler-node"]


ETHERNET_UNI = ("configure ethernet ont 1/1/6/1/1/1/1 cust-info Y33445566 auto-detect auto\n"
                "configure ethernet ont 1/1/6/1/1/1/1 admin-state up\n"
                "configure ethernet ont 1/1/6/1/1/1/2 cust-info Y00000000\n")


def test_ethernet_ont_deleted_resets_named_unis_and_named_fields_only(monkeypatch):
    def deleted(config):
        return run_module(monkeypatch, "isam_ethernet_onts", {"state": "deleted", "config": config}, ETHERNET_UNI)["commands"]

    # identity: every removable setting of that UNI (auto-detect has no 'no' form);
    # before, nothing was reset (lab ISAM)
    assert deleted([{"uni_idx": "1/1/6/1/1/1/1"}]) == [
        "configure ethernet ont 1/1/6/1/1/1/1 no cust-info no admin-state"]
    # named field: only that one (before, every setting of the UNI was reset)
    assert deleted([{"uni_idx": "1/1/6/1/1/1/1", "cust_info": "Y33445566"}]) == [
        "configure ethernet ont 1/1/6/1/1/1/1 no cust-info"]
    assert len(deleted(None)) == 2


@pytest.mark.parametrize("module, empty", [("isam_ethernet_onts", []), ("isam_ethernet_line", [])])
def test_gathered_from_an_empty_device_matches_the_config_type(monkeypatch, module, empty):
    """Lab ISAM: gathered of a removed UNI returned {} for the list-type ethernet_onts."""
    assert run_module(monkeypatch, module, {"state": "gathered"}, "")["gathered"] == empty


def test_targeted_gathered_finds_instances_with_only_default_settings(monkeypatch):
    """Lab ISAM: a trap manager at its default priority and an enabled trouble-shooting PON
    interface answer their single read with the header alone; flat detail shows them."""
    trap = "configure trap manager 192.0.2.1:162"
    device = {"info configure trap manager 192.0.2.1:162 flat detail": trap + " priority medium no cold-start-trap\n"}
    result = run_module(monkeypatch, "isam_traps", {"state": "gathered", "config": {"managers": [{"address": "192.0.2.1:162"}]}}, device)
    assert result["gathered"] == {"managers": [{"address": "192.0.2.1:162"}]}

    # trouble-shooting: the detail read of an enabled interface prints nothing either, an absent one fails
    single = "info configure trouble-shooting pon statistics interface %s flat"
    absent = Exception("Error : instance does not exist")

    def tsp_device(command):
        if command == (single % "1/1/6/3") + " detail":
            raise absent
        return "#---\necho \"statistics\"\n"
    config = {"interfaces": [{"name": "1/1/6/2"}, {"name": "1/1/6/3"}]}
    result = run_module(monkeypatch, "isam_trouble_shooting_pon", {"state": "gathered", "config": config}, tsp_device)
    assert result["gathered"] == {"interfaces": [{"name": "1/1/6/2"}]}


def test_qos_interface_profile_none_equals_the_unset_profile(monkeypatch):
    """Lab ISAM: after 'cac-profile none' the device omits cac-profile; merged re-sent it."""
    text = "configure qos interface pon:1/1/6/2 ds-num-rem-queue not-applicable us-num-queue not-applicable\n"
    result = run_module(monkeypatch, "isam_qos_interfaces", {"state": "merged", "config": [{"name": "pon:1/1/6/2", "cac_profile": "none"}]}, text)
    assert result["commands"] == []
    text = "configure qos interface pon:1/1/6/2 cac-profile name:FD_GponVideo\n"
    result = run_module(monkeypatch, "isam_qos_interfaces", {"state": "merged", "config": [{"name": "pon:1/1/6/2", "cac_profile": "none"}]}, text)
    assert result["commands"] == ["configure qos interface pon:1/1/6/2 cac-profile none"]
