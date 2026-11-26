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
        # boards cannot be removed ('no board' is an invalid token, lab ISAM): reset
        assert result["commands"] == ["configure xdsl board 1/1/1 no vce-profile", "configure xdsl board 1/1/3 no vce-profile"]
    named = run_module(monkeypatch, "isam_xdsl_boards",
                       {"state": "deleted", "config": {"boards": [{"board_id": "1/1/3"}]}}, text)
    assert named["commands"] == ["configure xdsl board 1/1/3 no vce-profile"]


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
    result = run_module(monkeypatch, module_name, {"state": "deleted"}, lab_captures.configured())
    assert not result.get("failed"), "%s: deleted failed" % module_name  # no message: it may quote config


def _lab_instances(monkeypatch):
    """(module, list path, identity) for one instance of every targetable list on the lab device."""
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.targeted import TARGETED_GATHER

    flat = lab_captures.configured()
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


XDSL_BOARD = ("configure xdsl board 1/1/6 dpbo-profile 4\n"
              "configure xdsl board 1/1/6 vect-fallback fb-vplt-com-fail\n"
              "configure xdsl board 1/1/3 dpbo-profile 1\n")


def test_xdsl_board_deleted_resets_attributes(monkeypatch):
    """Lab ISAM: 'configure xdsl no board <id>' is an invalid token; boards cannot be removed."""
    def deleted(config):
        return run_module(monkeypatch, "isam_xdsl_boards", {"state": "deleted", "config": config}, XDSL_BOARD)["commands"]

    assert deleted({"boards": [{"board_id": "1/1/6"}]}) == [
        "configure xdsl board 1/1/6 no dpbo-profile", "configure xdsl board 1/1/6 vect-fallback no fb-vplt-com-fail"]
    assert deleted({"boards": [{"board_id": "1/1/6", "dpbo_profile": "4"}]}) == ["configure xdsl board 1/1/6 no dpbo-profile"]
    assert not any("no board" in c for c in deleted(None))


PLANNED_SLOT = "configure equipment slot lt:1/1/6 planned-type ndlt-f unlock capab-profile 8vc_default\n"


def test_equipment_slot_unplanning_sends_only_no_planned_type(monkeypatch):
    """Lab ISAM: after 'no planned-type' the slot refuses 'no unlock' ("not yet planned", error 1)."""
    result = run_module(monkeypatch, "isam_equipment", {"state": "deleted", "config": {"slots": [{"id": "lt:1/1/6"}]}}, PLANNED_SLOT)
    assert result["commands"] == ["configure equipment slot lt:1/1/6 no planned-type"]


def test_equipment_slot_type_change_fails_before_any_command(monkeypatch):
    """Lab ISAM: 'planned-type <other>' on a planned slot: "needs to be unplanned first" (error 40)."""
    result = run_module(monkeypatch, "isam_equipment",
                        {"state": "merged", "config": {"slots": [{"id": "lt:1/1/6", "planned_type": "nelt-b"}]}}, PLANNED_SLOT)
    assert result.get("failed") and "Unplan it first with state deleted" in result["msg"]
    assert not result.get("commands")
    # planning an unplanned slot: the type alone (the device sets the capability profile itself)
    result = run_module(monkeypatch, "isam_equipment",
                        {"state": "merged", "config": {"slots": [{"id": "lt:1/1/6", "planned_type": "nelt-b", "unlock": True}]}},
                        "configure equipment slot lt:1/1/6 unlock\n")
    assert result["commands"] == ["configure equipment slot lt:1/1/6 planned-type nelt-b"]


def test_link_agg_group_keeps_its_default_member_port(monkeypatch):
    """Lab ISAM: 'link-agg group 1/1/6/3 no port 1/1/6/3' is refused (default aggregator, error 22)."""
    text = ("configure link-agg group 1/1/6/3 load-sharing-policy mac-dst mode static\n"
            "configure link-agg group 1/1/6/3 port 1/1/6/3\n"
            "configure link-agg group 1/1/6/3 port 1/1/6/4\n")
    commands = run_module(monkeypatch, "isam_link_agg", {"state": "deleted", "config": {"groups": [{"id": "1/1/6/3"}]}}, text)["commands"]
    assert "configure link-agg group 1/1/6/3 no port 1/1/6/4" in commands
    assert not any(c.endswith("no port 1/1/6/3") for c in commands), commands
    replaced = run_module(monkeypatch, "isam_link_agg",
                          {"state": "replaced", "config": {"groups": [{"id": "1/1/6/3", "mode": "static"}]}}, text)["commands"]
    assert not any(c.endswith("no port 1/1/6/3") for c in replaced), replaced


NAMED_FIELD_CASES = [
    ("isam_interfaces", "configure interface port pon:1/1/2/2 admin-up link-updown-trap\n",
     [{"name": "pon:1/1/2/2", "admin_up": False}], ["configure interface port pon:1/1/2/2 no admin-up"]),
    ("isam_link_agg", "configure link-agg port 1/1/8/1 passive-lacp short-timeout actor-port-prio 100\n",
     {"ports": [{"id": "1/1/8/1", "actor_port_prio": "100"}]}, ["configure link-agg port 1/1/8/1 no actor-port-prio"]),
    ("isam_xdsl_inm", "configure xdsl imp-noise-sensor near-end 1/1/6/3 inm-mode enable inm-iat-offset 10\n",
     {"near_end": [{"name": "1/1/6/3", "inm_mode": "enable"}]}, ["configure xdsl imp-noise-sensor near-end 1/1/6/3 no inm-mode"]),
    ("isam_xdsl_lines", "configure xdsl line 1/1/3/1 service-profile 13 spectrum-profile 2 admin-up\n",
     [{"name": "1/1/3/1", "admin_up": True}], ["configure xdsl line 1/1/3/1 no admin-up"]),
    ("isam_xstp", "configure xstp port 1/1/6/4 priority 64 edge-port path-cost 100000\n",
     {"ports": [{"port": "1/1/6/4", "priority": 64}]}, ["configure xstp port 1/1/6/4 no priority"]),
    ("isam_vlan_global", "configure vlan broadcast-frames priority-policy port-default\nconfigure vlan tpid 88a8\n"
     "configure vlan priority-regen 2 profile-name BestEffort pbit0 0 pbit1 0\n",
     {"priority_regen": [{"id": 2}]}, None),
]


@pytest.mark.parametrize("module, running, config, expected", NAMED_FIELD_CASES, ids=[c[0] for c in NAMED_FIELD_CASES])
def test_deleted_with_a_named_field_resets_only_that_field(monkeypatch, module, running, config, expected):
    """Found by a sweep over the lab capture: naming one field reset the whole instance."""
    commands = run_module(monkeypatch, module, {"state": "deleted", "config": config}, running)["commands"]
    if expected is not None:
        assert commands == expected
    else:  # vlan_global: a priority-regen entry must not reset other sections
        assert commands and not any("broadcast-frames" in c or "tpid" in c for c in commands), commands


def test_equipment_ont_deleted_with_a_named_field_keeps_the_ont(monkeypatch):
    """Found by the named-field sweep: naming desc1 removed the whole ONT."""
    running = ("configure equipment ont interface 1/1/5/1/3 sw-ver-pland disabled sernum ZZZZ:00000001 desc1 zztest\n"
               "configure equipment ont interface 1/1/5/1/3 admin-state up\n")

    def deleted(entry):
        return run_module(monkeypatch, "isam_equipment_onts", {"state": "deleted", "config": {"interfaces": [entry]}}, running)["commands"]
    assert deleted({"ont_idx": "1/1/5/1/3", "desc1": "zztest"}) == ["configure equipment ont interface 1/1/5/1/3 no desc1"]
    assert deleted({"ont_idx": "1/1/5/1/3"}) == ["configure equipment ont interface 1/1/5/1/3 admin-state down",
                                                 "configure equipment ont no interface 1/1/5/1/3"]


RENDER_FALSE_CASES = [
    ("isam_equipment", {"slots": [{"id": "lt:1/1/6", "unlock": False}]}, "configure equipment slot lt:1/1/6 no unlock"),
    ("isam_interfaces", [{"name": "pon:1/1/2/2", "admin_up": False}], "configure interface port pon:1/1/2/2 no admin-up"),
    ("isam_xdsl_lines", [{"name": "1/1/3/1", "admin_up": False}], "configure xdsl line 1/1/3/1 no admin-up"),
    ("isam_xstp", {"ports": [{"port": "1/1/6/4", "edge_port": False}]}, "configure xstp port 1/1/6/4 no edge-port"),
    ("isam_ethernet_line", [{"if_index": "1/1/6/1", "admin_up": False}], "configure ethernet line 1/1/6/1 no admin-up"),
]


@pytest.mark.parametrize("module, config, command", RENDER_FALSE_CASES, ids=[c[0] for c in RENDER_FALSE_CASES])
def test_rendered_renders_an_explicit_false(monkeypatch, module, config, command):
    """netcommon's compare() drops False without a device value; rendered must not."""
    assert command in run_module(monkeypatch, module, {"state": "rendered", "config": config})["rendered"]


def test_dhcp_server_lease_time_reset_is_sent_once(monkeypatch):
    result = run_module(monkeypatch, "isam_dhcp_server", {"state": "merged", "config": {"lease_time_enabled": False}},
                        "configure dhcp-server lease-time 3600\n")
    assert result["commands"].count("configure dhcp-server no lease-time") == 1, result["commands"]


VLAN_110 = ("configure vlan id 110 mode cross-connect name Internet new-broadcast enable protocol-filter pass-pppoe "
            "drly-srv-usr-side enable\n")


def test_vlan_merged_does_not_reset_unnamed_settings(monkeypatch):
    """Argspec defaults were injected: renaming a VLAN reset protocol-filter pass-pppoe to pass-all."""
    commands = run_module(monkeypatch, "isam_vlans", {"state": "merged", "config": [{"id": 110, "name": "Internet2"}]},
                          VLAN_110)["commands"]
    assert commands == ["configure vlan id 110 name Internet2"]


def test_vlan_deleted_named_setting_keeps_the_vlan_and_absent_vlans_are_skipped(monkeypatch):
    def deleted(config):
        return run_module(monkeypatch, "isam_vlans", {"state": "deleted", "config": config}, VLAN_110)["commands"]

    assert deleted([{"id": 110, "protocol-filter": "pass-pppoe"}]) == ["configure vlan id 110 no protocol-filter"]
    assert deleted([{"id": 110}]) == ["configure vlan no id 110"]
    assert deleted([{"id": 3999}]) == []


def test_l2cp_merged_without_partition_type_keeps_it(monkeypatch):
    running = "configure l2cp partition-type fixed-assigned\n"
    assert run_module(monkeypatch, "isam_l2cp", {"state": "merged", "config": [{"name": "l2cp"}]}, running)["commands"] == []
    assert run_module(monkeypatch, "isam_l2cp", {"state": "replaced", "config": [{"name": "l2cp"}]}, running)["commands"] == [
        "configure l2cp no partition-type"]


def test_ipv6_antispoofing_merged_keeps_and_replaced_resets_only_named_slots(monkeypatch):
    running = "configure ipv6-antispoofing slot 1/1/6 bit-len 128\nconfigure ipv6-antispoofing slot 1/1/7 bit-len 96\n"

    def commands(state, config):
        return run_module(monkeypatch, "isam_ipv6_antispoofing_slot", {"state": state, "config": config}, running)["commands"]

    assert commands("merged", [{"name": "1/1/6"}]) == []
    assert commands("replaced", [{"name": "1/1/6"}]) == ["configure ipv6-antispoofing slot 1/1/6 no bit-len"]
    assert commands("overridden", [{"name": "1/1/6", "bit_len": 128}]) == ["configure ipv6-antispoofing slot 1/1/7 no bit-len"]


def test_system_security_value_options_are_read_and_written_as_values(monkeypatch):
    """CLI guide: mixed-case, ssh access debug/debugkernel and tftp-rollovr take values; they were bool."""
    text = ("configure system security password min-length 6 mixed-case mandatory\n"
            "configure system security ssh access protocol ftp debug udp-ssh debugkernel ssh\n"
            "configure system security filetransfer protocol ftp tftp-rollovr 5\n")
    gathered = run_module(monkeypatch, "isam_system_security", {"state": "gathered"}, text)["gathered"]
    assert gathered["password"]["mixed_case"] == "mandatory"
    assert gathered["ssh"]["access"]["debug"] == "udp-ssh" and gathered["ssh"]["access"]["debugkernel"] == "ssh"
    assert gathered["filetransfer"]["tftp_rollovr"] == 5
    rendered = run_module(monkeypatch, "isam_system_security", {"state": "rendered", "config": {"password": {"mixed_case": "mandatory"}}})
    assert rendered["rendered"] == ["configure system security password mixed-case mandatory"]


def test_system_value_options_are_read_and_written_as_values(monkeypatch):
    """CLI guide: these were modelled as flags; values were lost on read and rendered bare."""
    text = ("configure system id DS name x location y system-40gkr4 enable periph-mgnt-ctrl enable\n"
            "configure system external-leds status disable\n"
            "configure system auto-switch xdsl-stepup-delay 1800\n"
            "configure system pon-ont sw-ver-mis-block disable sn-autounlock enable\n"
            "configure system sync-if-timing ais-sensitivity enable\n")
    got = run_module(monkeypatch, "isam_system", {"state": "gathered"}, text)["gathered"]
    assert got["id"]["system_40gkr4"] == "enable" and got["id"]["periph_mgnt_ctrl"] == "enable"
    assert got["external_leds"] == {"status": "disable"} and got["auto_switch"] == {"xdsl_stepup_delay": 1800}
    assert got["pon_ont"] == {"sw_ver_mis_block": "disable", "sn_autounlock": "enable"}
    assert got["sync_if_timing"]["ais_sensitivity"] == "enable"
    rendered = run_module(monkeypatch, "isam_system", {"state": "rendered", "config": {
        "external_leds": {"status": "disable"}, "auto_switch": {"xdsl_stepup_delay": 1800}}})["rendered"]
    assert rendered == ["configure system external-leds status disable", "configure system auto-switch xdsl-stepup-delay 1800"]


# --- isam_voice_sip: rebuilt on one grammar table (value options were bool flags) ---

VSIP_LAB = (
    'configure voice sip lineid-syn-prof profile1 isdn-syntax ""\n'
    "configure voice sip vsp vsp1 domain-name DomainName.com no ta4 timer-b 32000 timer-t1 500\n"
    "configure voice sip register vsp1 no register-intv\n"
    "configure voice sip redundancy vsp1 no support-redun\n"
    "configure voice sip system session-timer no status no se-time\n"
    "configure voice sip redundancy-cmd vsp1 fail-x-type geo-fail-over\n"
    "configure voice sip statistics no cdr-config\n"
    "configure voice sip statistics stats-config per-line no out-180-rsp\n"
    'configure voice sip cas-nsm-prof common-cas-profile international-prefix "#" country-code "#" outg-cpn-length 0\n'
)


def _vsip(monkeypatch, state, config=None, running=VSIP_LAB):
    args = {"state": state} if config is None else {"state": state, "config": config}
    return run_module(monkeypatch, "isam_voice_sip", args, running)


def test_voice_sip_value_options_are_read_as_values(monkeypatch):
    """Data loss before: ta4 5000 and digit-send-mode overlap-invite were read as True."""
    running = "configure voice sip vsp vsp1 domain-name d ta4 5000 digit-send-mode overlap-invite\n"
    vsp = _vsip(monkeypatch, "gathered", running=running)["gathered"]["vsp"][0]
    assert vsp["ta4"] == 5000 and vsp["digit_send_mode"] == "overlap-invite"
    assert _vsip(monkeypatch, "merged", {"vsp": [{"name": "vsp1", "ta4": 6000}]}, running=running)["commands"] == [
        "configure voice sip vsp vsp1 ta4 6000"]
    # a value equal to the device default resets it when set, and is a no-op when already default
    assert _vsip(monkeypatch, "merged", {"vsp": [{"name": "vsp1", "ta4": 4000}]}, running=running)["commands"] == [
        "configure voice sip vsp vsp1 no ta4"]
    assert _vsip(monkeypatch, "merged", {"vsp": [{"name": "vsp1", "ta4": 4000}]}, running="configure voice sip vsp vsp1 domain-name d\n")["commands"] == []


def test_voice_sip_gathered_is_idempotent_and_round_trips(monkeypatch):
    gathered = _vsip(monkeypatch, "gathered")["gathered"]
    assert _vsip(monkeypatch, "merged", gathered)["commands"] == []
    assert _vsip(monkeypatch, "replaced", gathered)["commands"] == []
    rendered = _vsip(monkeypatch, "rendered", gathered)["rendered"]
    reparsed = run_module(monkeypatch, "isam_voice_sip",
                          {"state": "parsed", "running_config": "\n".join(rendered)})["parsed"]
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.voice_sip import TABLE
    assert TABLE.without_defaults(reparsed) == gathered


def test_voice_sip_deleted_scoping(monkeypatch):
    running = "configure voice sip vsp vsp1 domain-name d ta4 5000\nconfigure voice sip register vsp1 no register-intv\n"
    # naming an attribute resets only it; naming the instance removes the whole instance
    assert _vsip(monkeypatch, "deleted", {"vsp": [{"name": "vsp1", "ta4": 5000}]}, running=running)["commands"] == [
        "configure voice sip vsp vsp1 no ta4"]
    assert _vsip(monkeypatch, "deleted", {"vsp": [{"name": "vsp1"}]}, running=running)["commands"] == [
        "configure voice sip no vsp vsp1"]
    # naming one section never touches another
    assert _vsip(monkeypatch, "deleted", {"register": [{"name": "vsp1"}]}, running=running)["commands"] == [
        "configure voice sip no register vsp1"]


def test_voice_sip_creation_requires_mandatory_values(monkeypatch):
    res = _vsip(monkeypatch, "merged", {"vsp": [{"name": "new"}]}, running="")
    assert res.get("failed") and "domain_name" in res["msg"]
    res = _vsip(monkeypatch, "merged", {"cas_nsm_prof": [{"name": "c"}]}, running="")
    assert res.get("failed") and "international_prefix" in res["msg"]


def test_voice_sip_table_argspec_and_documentation_agree():
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.voice_sip.voice_sip import Isam_voice_sipArgs
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.voice_sip import TABLE
    from ansible_collections.nokia.isam.plugins.modules import isam_voice_sip

    from .table_agreement import assert_table_matches
    assert_table_matches(TABLE, Isam_voice_sipArgs.argument_spec, isam_voice_sip.DOCUMENTATION)


def test_explicit_default_resets_to_default(monkeypatch):
    """Setting a value back to its device default must reset it (not be a silent no-op):
    merged sends the no-form when the device is non-default, and nothing when already default."""
    # generic_pon: ont slid-mode default ascii
    run = "configure generic-pon ont slid-mode hexa-dec\n"
    assert run_module(monkeypatch, "isam_generic_pon", {"state": "merged", "config": {"ont": {"slid_mode": "ascii"}}}, run)["commands"] == [
        "configure generic-pon ont no slid-mode"]
    assert run_module(monkeypatch, "isam_generic_pon", {"state": "merged", "config": {"ont": {"slid_mode": "ascii"}}}, "")["commands"] == []
    # voice_sip: vsp auto-verify-like value (reg-sub default disable)
    run = "configure voice sip vsp vsp1 domain-name d reg-sub enable\n"
    assert run_module(monkeypatch, "isam_voice_sip", {"state": "merged", "config": {"vsp": [{"name": "vsp1", "reg_sub": "disable"}]}}, run)["commands"] == [
        "configure voice sip vsp vsp1 no reg-sub"]
    # software_mngt: oswp auto-verify default disabled
    run = "configure software-mngt oswp 1 primary-file-server-id 1.2.3.4 second-file-server-id 0.0.0.0 auto-verify enabled\n"
    assert run_module(monkeypatch, "isam_software_mngt", {"state": "merged", "config": {"oswp": [{"id": "1", "auto_verify": "disabled"}]}}, run)["commands"] == [
        "configure software-mngt oswp 1 no auto-verify"]


# --- isam_software_mngt: rebuilt on one grammar table (value options were bool flags) ---

SWMNGT_LAB = (
    "configure software-mngt sw-replacement-mode upgrade-via-standby\n"
    "configure software-mngt oswp 1 primary-file-server-id 192.0.2.11 second-file-server-id 0.0.0.0 no activate no auto-verify no on-schedule-time\n"
    "configure software-mngt database no activate backup activate:192.0.2.10:backup/ backupv6 activate:::/backup/ no auto-backup-intvl\n"
)


def _swmngt(monkeypatch, state, config=None, running=SWMNGT_LAB):
    args = {"state": state} if config is None else {"state": state, "config": config}
    return run_module(monkeypatch, "isam_software_mngt", args, running)


def test_software_mngt_value_options_are_read_as_values(monkeypatch):
    """Data loss before: activate after-download / auto-verify enabled were read as True."""
    running = "configure software-mngt oswp 1 primary-file-server-id 192.0.2.1 second-file-server-id 0.0.0.0 activate after-download auto-verify enabled\n"
    o = _swmngt(monkeypatch, "gathered", running=running)["gathered"]["oswp"][0]
    assert o["activate"] == "after-download" and o["auto_verify"] == "enabled"
    assert _swmngt(monkeypatch, "merged", {"oswp": [{"id": "1", "auto_verify": "enabled"}]}, running=running)["commands"] == []


def test_software_mngt_gathered_is_idempotent_and_round_trips(monkeypatch):
    gathered = _swmngt(monkeypatch, "gathered")["gathered"]
    assert _swmngt(monkeypatch, "merged", gathered)["commands"] == []
    assert _swmngt(monkeypatch, "replaced", gathered)["commands"] == []
    rendered = _swmngt(monkeypatch, "rendered", gathered)["rendered"]
    reparsed = run_module(monkeypatch, "isam_software_mngt",
                          {"state": "parsed", "running_config": "\n".join(rendered)})["parsed"]
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.software_mngt import TABLE
    assert TABLE.without_defaults(reparsed) == gathered


def test_software_mngt_deleted_scoping(monkeypatch):
    running = ("configure software-mngt oswp 1 primary-file-server-id 192.0.2.1 second-file-server-id 0.0.0.0 auto-verify enabled\n"
               "configure software-mngt oswp 2 primary-file-server-id 192.0.2.2 second-file-server-id 0.0.0.0\n")
    # naming an attribute resets only it; naming the instance removes it; siblings untouched
    assert _swmngt(monkeypatch, "deleted", {"oswp": [{"id": "1", "auto_verify": "enabled"}]}, running=running)["commands"] == [
        "configure software-mngt oswp 1 no auto-verify"]
    assert _swmngt(monkeypatch, "deleted", {"oswp": [{"id": "1"}]}, running=running)["commands"] == [
        "configure software-mngt no oswp 1"]


def test_software_mngt_table_argspec_and_documentation_agree():
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.software_mngt.software_mngt import Software_mngtArgs
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.software_mngt import TABLE
    from ansible_collections.nokia.isam.plugins.modules import isam_software_mngt

    from .table_agreement import assert_table_matches
    assert_table_matches(TABLE, Software_mngtArgs.argument_spec, isam_software_mngt.DOCUMENTATION)