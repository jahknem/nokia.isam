"""0.3.14 must fix the released APIs, not accidentally publish the feature branch.

The action-module failure serialization through the real module entrypoint lives in
test_action_failure_entrypoint.py.
"""
import hashlib
import json
from pathlib import Path
import runpy

import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import get_scoped_config, _targeted_reply

from .module_runner import run_module


ROOT = Path(__file__).resolve().parents[5]


def _without_defaults(value):
    if isinstance(value, dict):
        return {key: _without_defaults(item) for key, item in value.items() if key != "default"}
    if isinstance(value, (list, tuple)):
        return [_without_defaults(item) for item in value]
    return value


def test_argument_surface_matches_0_3_13_except_device_defaults():
    # Generated from every argspec in tag 0.3.13, not from feature HEAD. Include
    # types, choices, aliases, required flags and option names recursively. Only
    # defaults are excluded: removing injected device defaults is an intentional fix.
    specs = {}
    for path in sorted((ROOT / "plugins/module_utils/network/isam/argspec").rglob("*.py")):
        if path.name == "__init__.py":
            continue
        namespace = runpy.run_path(str(path))
        specs[path.relative_to(ROOT).as_posix()] = {
            name: _without_defaults(cls.argument_spec)
            for name, cls in namespace.items() if isinstance(cls, type) and hasattr(cls, "argument_spec")
        }
    # The 1.0 feature split migrates these families intentionally (one family PR
    # each): their argspecs are excluded from the frozen 0.3.13 surface here and
    # re-locked by their PR's api_baseline.json. The integration PR that lands the
    # whole stack replaces this file with test_release_regressions.py, which keeps
    # the 0.3.14 safety regressions without the pre-1.0 lock.
    # Names are the argspec directories (vlan_global, not isam_vlan_global).
    migrated = {"ani_onts", "equipment_onts", "equipment_replan", "ethernet_onts", "generic_pon",
                "interface_alarms", "isam_equipment", "vlan_global", "ntp_onts",
                "pon_interfaces", "pon_global", "trouble_shooting_pon", "l2uni_onts", "uni_onts",
                "qos_global", "qos_interfaces", "qos_maps", "qos_profiles", "qos_tca",
                "software_mngt", "vlans", "voice_sip", "system_security", "security_ext_authenticator",
                "bridge_learned_mac", "cwmp_plt", "dhcp_relay_port_stats", "error", "ethernet_statistics",
                "nat", "pppox_relay_global", "xdsl_boards", "xdsl_inm", "xdsl_lines", "xdsl_onts",
                "xdsl_profiles", "xdsl_system",
                "ihub_common", "ihub_lags", "ihub_ports", "ihub_services"}
    # A shared argspec at the top of argspec/ (ihub_common.py) is named by its file stem.
    specs = dict((path, spec) for path, spec in specs.items()
                 if path.split("/")[-2] not in migrated and Path(path).stem not in migrated)
    # The same 33 argspecs computed from tag 0.3.13 give this hash.
    assert len(specs) == 33
    assert hashlib.sha256(json.dumps(specs, sort_keys=True).encode()).hexdigest() == (
        "6f5e85c25d01f89f6fb4defda4e4df16d38da19f2de9d37f58012a98c2904b54")


def test_module_inventory_matches_0_3_13():
    paths = sorted(path.relative_to(ROOT).as_posix() for path in (ROOT / "plugins/modules").rglob("*.py"))
    # The 1.0 feature split adds modules intentionally (one family PR each): the
    # released 0.3.13 inventory must survive unchanged (no removals, no renames).
    added_by_the_split = {
        "plugins/modules/isam_l2uni_onts.py",
        "plugins/modules/isam_pon_global.py",
        "plugins/modules/isam_qos_global.py",
        "plugins/modules/isam_qos_tca.py",
        "plugins/modules/isam_system_security.py",
        "plugins/modules/isam_ihub_lags.py",
        "plugins/modules/isam_ihub_ports.py",
        "plugins/modules/isam_ihub_services.py",
        "plugins/modules/isam_topology_discovery.py",
        "plugins/modules/isam_bridge_learned_mac.py",
        "plugins/modules/isam_cwmp_plt.py",
        "plugins/modules/isam_dhcp_relay_port_stats.py",
        "plugins/modules/isam_error.py",
        "plugins/modules/isam_ethernet_statistics.py",
        "plugins/modules/isam_nat.py",
        "plugins/modules/isam_pppox_relay_global.py",
        "plugins/modules/isam_xdsl_inm.py",
        "plugins/modules/isam_xdsl_onts.py",
        "plugins/modules/isam_xdsl_system.py",
        "plugins/modules/isam_trouble_shooting_pon.py",
        "plugins/modules/isam_uni_onts.py",
    }
    pre_split = [path for path in paths if path not in added_by_the_split]
    assert len(paths) == len(pre_split) + 21
    assert hashlib.sha256("\n".join(pre_split).encode()).hexdigest() == (
        "88ec8c7f4f4ed973e1ddd0591b2f137aada9331d42e9e633307a7f257b9d8827")


@pytest.mark.parametrize("section,node", [("lineid_syn_prof", "lineid-syn-prof"), ("vsp", "vsp"),
                                          ("register", "register"), ("redundancy", "redundancy"),
                                          ("redundancy_cmd", "redundancy-cmd"), ("cas_nsm_prof", "cas-nsm-prof")])
def test_sip_replaced_preserves_unnamed_instances_but_overridden_removes_them(monkeypatch, section, node):
    running = "configure voice sip %s first\nconfigure voice sip %s second\n" % (node, node)
    config = {section: [{"name": "first"}]}
    for state in ("replaced", "overridden"):
        result = run_module(monkeypatch, "isam_voice_sip", {"state": state, "config": config}, running)
        assert not result.get("failed"), result.get("msg")
        assert result["commands"] == ([] if state == "replaced" else ["configure voice sip no %s second" % node])


def test_software_replaced_already_preserves_unnamed_oswps(monkeypatch):
    running = "configure software-mngt oswp 1 auto-verify\nconfigure software-mngt oswp 2 auto-verify\n"
    # auto-verify is a value option in the rebuilt table schema (disabled/enabled).
    result = run_module(monkeypatch, "isam_software_mngt", {"state": "replaced", "config": {"oswp": [{"id": "1", "auto_verify": "enabled"}]}}, running)
    assert not result.get("failed"), result.get("msg")
    assert not any("oswp 2" in command for command in result["commands"])


@pytest.mark.parametrize("state", ["merged", "replaced"])
def test_linetest_configured_replay_is_idempotent(monkeypatch, state):
    running = ("configure linetest single ltsession 3 timeout-period 120\n"
               "configure linetest single ltparm 3 resistance value1 12\n")
    config = run_module(monkeypatch, "isam_linetest", {"state": "parsed", "running_config": running})["parsed"]
    result = run_module(monkeypatch, "isam_linetest", {"state": state, "config": config}, running)
    assert result["commands"] == []


def test_linetest_omissions_are_not_resets_and_removed_session_owns_its_parameters(monkeypatch):
    running = ("configure linetest single ltsession 3 group-opt single\n"
               "configure linetest single ltparm 3 resistance value1 12\n")
    for state in ("merged", "rendered"):
        result = run_module(monkeypatch, "isam_linetest", {"state": state, "config": {"sessions": [{"session_id": "3"}]}}, running)
        assert result["rendered" if state == "rendered" else "commands"] == []
    result = run_module(monkeypatch, "isam_linetest", {"state": "overridden", "config": {"sessions": []}}, running)
    assert result["commands"] == ["configure linetest single ltsession 3 session-cmd destroy"]


CFM = "configure cfm domain 200 name string:zztest level 3\nconfigure cfm slm inactivity-time 20\n"


@pytest.mark.parametrize("state", ["merged", "replaced"])
def test_cfm_remote_mep_and_pm_replay_is_idempotent(monkeypatch, state):
    running = CFM + (
        "configure cfm domain 200 association 1 vlan 3990\n"
        "configure cfm domain 200 association 1 remote-mep 11\n"
        "configure cfm domain 200 association 1 mep 10 ccm-priority 5\n"
        "configure cfm domain 200 association 1 mep 10 active-remote-mep 11\n"
        "configure cfm y1731pm domain 200 association 1 mep 10 session-id 2 type dmm target-mac 02:00:00:00:00:11 priority 5\n")
    config = run_module(monkeypatch, "isam_cfm", {"state": "parsed", "running_config": running})["parsed"]
    result = run_module(monkeypatch, "isam_cfm", {"state": state, "config": config}, running)
    assert result["commands"] == []


def test_cfm_slm_and_domain_scope_are_independent(monkeypatch):
    result = run_module(monkeypatch, "isam_cfm", {"state": "deleted", "config": {"slm": {"inactivity_time": 20}}}, CFM)
    assert result["commands"] == ["configure cfm slm no inactivity-time"]
    config = {"domains": [{"domain_index": 200, "name": "string:zztest", "level": 3}]}
    result = run_module(monkeypatch, "isam_cfm", {"state": "replaced", "config": config}, CFM)
    assert result["commands"] == []
    config["domains"][0]["name"] = "string:changed"
    result = run_module(monkeypatch, "isam_cfm", {"state": "replaced", "config": config}, CFM)
    assert result["failed"] and "cannot be modified" in result["msg"]
    assert not result.get("commands")


def test_generic_pon_nested_delete_does_not_reset_parent_or_other_sections(monkeypatch):
    running = ("configure generic-pon utilization pon-pmcollect pm-enable\n"
               "configure generic-pon utilization threshold txmcutilhi 10\n"
               "configure generic-pon ont slid-mode hexa-dec\n")
    config = {"utilization": {"threshold": {"txmcutilhi": "10"}}}
    result = run_module(monkeypatch, "isam_generic_pon", {"state": "deleted", "config": config}, running)
    assert result["commands"] == ["configure generic-pon utilization threshold no txmcutilhi"]
    result = run_module(monkeypatch, "isam_generic_pon", {"state": "replaced", "config": {"utilization": {"pon_pmcollect": "pm-enable"}}}, running)
    assert not any(" ont " in command for command in result["commands"])


def test_gathered_efm_oam_never_reconciles_the_requested_config(monkeypatch):
    result = run_module(monkeypatch, "isam_efm_oam_interface",
                        {"state": "gathered", "config": [{"name": "1/1/6/5", "admin_up": False}]},
                        "configure efm-oam interface 1/1/6/5 admin-up response-intvl 7\n")
    assert result["gathered"][0]["admin_up"] is True
    assert not result.get("commands") and not result["changed"]


def test_vlan_legacy_keys_render_identifiers_and_double_quoted_names(monkeypatch):
    config = [{"id": "3990", "mode": "residential-bridge", "name": "Test VLAN",
               "dhcpv6-itf-id": "physical-id", "dhcpv6-remote-id": "customer-id"}]
    result = run_module(monkeypatch, "isam_vlans", {"state": "rendered", "config": config})
    commands = "\n".join(result["rendered"])
    assert 'name "Test VLAN"' in commands
    assert "dhcpv6-itf-id physical-id" in commands and "dhcpv6-remote-id customer-id" in commands
    result = run_module(monkeypatch, "isam_vlans", {"state": "merged", "config": [{"id": "3990", "name": "Test VLAN"}]})
    assert result["failed"] and "mode is required to create it" in result["msg"]


def test_alarm_description_quotes_hash_and_embedded_quotes(monkeypatch):
    result = run_module(monkeypatch, "isam_alarm", {"state": "rendered", "config": {
        "custom_profiles": [{"name": "zztest", "description1": '#test "quoted"'}]}})
    assert result["rendered"] == ['configure alarm custom-profile zztest description1 "#test \\"quoted\\""']


def test_targeted_echo_bare_instance_and_duplicate_read_handling():
    command = "info configure ani ont tca-thresh 1/1/2/1/100 flat"
    header = '#---\necho "ani"\n'
    assert _targeted_reply(command, command[:-2] + "\nat\n" + header) == ""

    class Module:
        params = {"state": "gathered"}

    class Device:
        calls = []

        def get(self, cmd):
            self.calls.append(cmd)
            return "configure ani ont tca-thresh 1/1/2/1/100 no lower-optical-th\n" if cmd.endswith(" detail") else header

    device = Device()
    result = get_scoped_config(Module(), device, None, "unused", [command, command], bare_commands=[command])
    assert result == "configure ani ont tca-thresh 1/1/2/1/100\n"
    assert device.calls == [command, command + " detail"]


@pytest.mark.parametrize("entry", [{"port": "1/1/6/1"}, {"port": "1/1/6/1\n", "clear_statistics": True},
                                    {"port": "1/1/6/1;exit", "clear_statistics": True}])
def test_action_requires_an_explicit_operation_and_safe_identifier(monkeypatch, entry):
    result = run_module(monkeypatch, "isam_security_ext_authenticator", {"config": [entry]})
    assert result["failed"] and not result.get("commands")
