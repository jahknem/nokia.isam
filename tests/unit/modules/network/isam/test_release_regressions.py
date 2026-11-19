"""Carry 0.3.14 safety regressions forward with the explicitly migrated 1.0 schemas."""
import json

import pytest

from ansible_collections.nokia.isam.plugins.modules import isam_security_ext_authenticator
from ansible_collections.nokia.isam.plugins.module_utils.network.isam import action_module
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.bridges.bridges import Bridges
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import get_scoped_config, _targeted_reply

from .isam_module import set_module_args
from .module_runner import run_module


def test_bridge_merge_preserves_device_and_request_order():
    have = {"second": {"id": "second"}, "first": {"id": "first"}}
    want = {"third": {"id": "third"}, "first": {"id": "first"}}
    assert list(Bridges._merge_ports(have, want)) == ["second", "first", "third"]


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
    running = "configure software-mngt oswp 1 auto-verify enabled\nconfigure software-mngt oswp 2 auto-verify enabled\n"
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
    assert result["failed"] and "mode" in result["msg"]


def test_alarm_description_quotes_hash_and_embedded_quotes(monkeypatch):
    result = run_module(monkeypatch, "isam_alarm", {"state": "rendered", "config": {
        "custom_profiles": [{"name": "zztest", "description1": '#test "quoted"'}]}})
    assert result["rendered"] == ['configure alarm custom-profile zztest description1 "#test \\"quoted\\""']


@pytest.mark.parametrize("name", ["Plain", "#Example", 'Example "quoted"'])
def test_vlan_name_render_parse_preserves_special_characters(monkeypatch, name):
    config = [{"id": "3990", "mode": "residential-bridge", "name": name}]
    rendered = run_module(monkeypatch, "isam_vlans", {"state": "rendered", "config": config})["rendered"]
    parsed = run_module(monkeypatch, "isam_vlans", {"state": "parsed", "running_config": "\n".join(rendered)})["parsed"]
    assert parsed[0]["name"] == name


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


def test_action_partial_failure_uses_real_ansible_json_without_retry(monkeypatch, capsys):
    commands = ["admin security ext-authenticator 1/1/6/%s clear-statistics" % port for port in (1, 2, 3)]

    class Connection:
        calls = []

        def edit_config(self, candidate):
            self.calls.append(candidate)
            if candidate == [commands[1]]:
                raise RuntimeError("device refused command")
            return {"response": ["accepted"]}

    connection = Connection()
    monkeypatch.setattr(action_module, "get_resource_connection", lambda module: connection)
    set_module_args({"config": [{"port": "1/1/6/%s" % port, "clear_statistics": True} for port in (1, 2, 3)]}, True)
    with pytest.raises(SystemExit) as exited:
        isam_security_ext_authenticator.main()
    assert exited.value.code == 1
    result = json.loads(capsys.readouterr().out)
    assert result["failed"] is True and result["changed"] is True
    assert result["failed_command"] == commands[1]
    assert result["completed"] == [commands[0]] and result["pending"] == [commands[2]]
    assert result["response"] == ["accepted"]
    assert connection.calls == [[commands[0]], [commands[1]]]


def test_action_connection_failure_is_unchanged_with_real_ansible_json(monkeypatch, capsys):
    def unavailable(module):
        raise RuntimeError("connection unavailable")

    monkeypatch.setattr(action_module, "get_resource_connection", unavailable)
    set_module_args({"config": [{"port": "1/1/6/1", "clear_statistics": True}]}, True)
    with pytest.raises(SystemExit) as exited:
        isam_security_ext_authenticator.main()
    assert exited.value.code == 1
    result = json.loads(capsys.readouterr().out)
    assert result["failed"] is True and result["changed"] is False
    assert "acquire a connection" in result["msg"]


@pytest.mark.parametrize("entry", [{"port": "1/1/6/1"}, {"port": "1/1/6/1\n", "clear_statistics": True},
                                    {"port": "1/1/6/1;exit", "clear_statistics": True}])
def test_action_requires_an_explicit_operation_and_safe_identifier(monkeypatch, entry):
    result = run_module(monkeypatch, "isam_security_ext_authenticator", {"config": [entry]})
    assert result["failed"] and not result.get("commands")
