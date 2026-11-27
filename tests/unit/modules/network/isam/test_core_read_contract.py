"""Shared targeted-read semantics, independent of any resource parser."""
from types import SimpleNamespace

import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import get_scoped_config, get_targeted_config
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.read_outcomes import ReadOutcomeCollector


COMMAND = "info configure example interface 1/1/1/1 flat"
PATH = "configure example interface 1/1/1/1"


class Device:
    def __init__(self, detail):
        self.detail = detail
        self.commands = []

    def get(self, command):
        self.commands.append(command)
        if command.endswith(" detail"):
            if isinstance(self.detail, Exception):
                raise self.detail
            return self.detail
        return command + "\n#----------------\n"


def read(device, **kwargs):
    collector = ReadOutcomeCollector("example")
    module = SimpleNamespace(params={"state": "gathered"})
    result = get_scoped_config(module, device, None, None, [COMMAND],
                               outcomes=collector, selectors={COMMAND: [("config", "1/1/1/1")]}, **kwargs)
    return result, collector.to_result()


def test_default_only_instance_is_probed_without_family_opt_in():
    device = Device(PATH + " no enabled no profile\n")
    result, outcomes = read(device)
    assert result == PATH + "\n"
    assert device.commands == [COMMAND, COMMAND + " detail"]
    assert outcomes["outcomes"][0]["existence"] == "present"
    assert "no enabled" not in result  # firmware defaults are not configuration


@pytest.mark.parametrize("detail", ["", "echo example\n#-------------\n", "Error : instance does not exist"])
def test_a_missing_instance_is_confirmed_absent_by_its_detail_read(detail):
    # 'flat detail' prints every existing instance: header only there, or the device's
    # explicit error, proves absence (DS-LIN-TEST-01 2026-11-27, 52 missing instances).
    result, outcomes = read(Device(detail))
    assert result == ""
    assert outcomes["outcomes"][0]["existence"] == "confirmed_absent"


def test_a_missing_instance_reported_as_exception_is_confirmed_absent():
    result, outcomes = read(Device(Exception("Error : instance does not exist")))
    assert outcomes["outcomes"][0]["existence"] == "confirmed_absent"


@pytest.mark.parametrize("detail, command", [
    ("Error : invalid token", "rejected"),
    ("Error : lower-interface does not exist", "ok"),
    ("configure example interface 1/1/1/10 no enabled\n", "ok"),
])
def test_an_inconclusive_detail_read_proves_nothing(detail, command):
    result, outcomes = read(Device(detail))
    assert result == ""
    assert outcomes["outcomes"][0]["existence"] == "unknown"
    assert outcomes["outcomes"][0]["command"] == command


def test_a_silent_switch_is_present_when_its_detail_read_is_empty():
    # isam_arp_relay statistics: on -> header only, also with detail; off -> explicit error.
    result, outcomes = read(Device(""), silent_bare_commands=(COMMAND,))
    assert result == PATH + "\n" and outcomes["outcomes"][0]["existence"] == "present"
    _, outcomes = read(Device("Error : instance does not exist"), silent_bare_commands=(COMMAND,))
    assert outcomes["outcomes"][0]["existence"] == "confirmed_absent"


@pytest.mark.parametrize("detail", ["", "Error : instance does not exist"])
def test_an_unobservable_setting_is_never_confirmed_absent(detail):
    _, outcomes = read(Device(detail), unobservable_commands=(COMMAND,))
    assert outcomes["outcomes"][0]["existence"] == "unknown"


def test_the_policies_come_from_the_central_table():
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.targeted import absence_policy
    assert absence_policy("isam_arp_relay", "config") == "silent"
    assert absence_policy("isam_dhcp_relay", "config") == "unobservable"
    assert absence_policy("efm_oam_interface", "config") is None
    assert absence_policy("trouble_shooting_pon", "interfaces") == "silent"


def test_shared_node_check_does_not_trigger_single_instance_probe():
    device = Device(PATH + " no enabled\n")
    result, _ = read(device, instance_checks={("config", "1/1/1/1"): lambda reply: False})
    assert result == ""
    assert device.commands == [COMMAND]


def test_write_comparison_does_not_gain_implicit_detail_reads():
    device = Device(PATH + " no enabled\n")
    module = SimpleNamespace(params={"state": "merged"})
    assert get_scoped_config(module, device, None, None, [COMMAND]) == ""
    assert device.commands == [COMMAND]


def test_empty_absence_requires_explicit_single_instance_policy():
    device = Device(AssertionError("must not need a detail read"))
    result, outcomes = read(device, empty_absent_commands=(COMMAND,))
    assert result == ""
    assert outcomes["outcomes"][0]["existence"] == "confirmed_absent"
    assert device.commands == [COMMAND]


def test_detail_transport_failure_is_sanitized_and_fails_the_read():
    saved = {}

    def fail_json(**result):
        saved.update(result)
        raise RuntimeError("module failed")

    module = SimpleNamespace(params={"state": "gathered"}, fail_json=fail_json)
    collector = ReadOutcomeCollector("example")
    with pytest.raises(RuntimeError, match="module failed"):
        get_scoped_config(module, Device(Exception("connection lost PRIVATE PAYLOAD")),
                          None, None, [COMMAND], outcomes=collector,
                          selectors={COMMAND: [("config", "1/1/1/1")]})
    assert "PRIVATE PAYLOAD" not in str(saved)
    outcome = saved["read_outcomes"]["outcomes"][0]
    assert outcome["command"] == "failed"
    assert outcome["existence"] == "unknown"


def test_shared_command_runs_once_and_attributes_each_selector_separately():
    module = SimpleNamespace(params={"state": "gathered", "config": [{"name": "a"}, {"name": "b"}]})
    commands = []

    def get(command):
        commands.append(command)
        return "configure example member a enabled\n"

    get_targeted_config(module, SimpleNamespace(get=get), "interfaces", "unused",
                        {"config": lambda identity: ["info configure example flat"]},
                        instance_checks={"config": lambda reply, identity: "member %s " % identity in reply})
    assert commands == ["info configure example flat"]
    outcomes = module._isam_read_outcomes["outcomes"]
    assert [(r["selector"], r["existence"]) for r in outcomes] == [("a", "present"), ("b", "unknown")]


@pytest.mark.parametrize("config", [[{}], [{"name": "a"}, {}], [{"name": "a\nconfigure example"}]])
def test_incomplete_or_injected_selector_sends_no_commands(config):
    module = SimpleNamespace(params={"state": "gathered", "config": config})
    device = Device("")
    with pytest.raises((RuntimeError, ValueError)):
        get_targeted_config(module, device, "interfaces", "info configure example flat",
                            {"config": "info configure example interface %s flat"})
    assert device.commands == []


DETAIL_COMMAND = COMMAND + " detail"


def read_detail(reply, **kwargs):
    """A gathered single-instance read whose command already is 'flat detail'."""
    device = SimpleNamespace(commands=[])

    def get(command):
        device.commands.append(command)
        return command + "\n" + reply
    device.get = get
    collector = ReadOutcomeCollector("example")
    module = SimpleNamespace(params={"state": "gathered"})
    result = get_scoped_config(module, device, None, None, [DETAIL_COMMAND],
                               outcomes=collector, selectors={DETAIL_COMMAND: [("config", "1/1/1/1")]}, **kwargs)
    return result, collector.to_result()["outcomes"][0], device.commands


@pytest.mark.parametrize("reply", ["", "#----------------\n"])
def test_a_header_only_detail_read_is_confirmed_absent_without_a_second_read(reply):
    result, outcome, commands = read_detail(reply)
    assert result == "" and commands == [DETAIL_COMMAND]
    assert outcome["existence"] == "confirmed_absent"


def test_a_detail_read_with_the_instance_is_present():
    _, outcome, _ = read_detail(PATH + " no enabled\n")
    assert outcome["existence"] == "present"


@pytest.mark.parametrize("policy", ["silent_bare_commands", "unobservable_commands"])
def test_a_header_only_detail_read_under_a_policy_proves_nothing(policy):
    _, outcome, _ = read_detail("", **{policy: (DETAIL_COMMAND,)})
    assert outcome["existence"] == "unknown"


def test_a_header_only_detail_read_in_a_write_state_is_not_classified():
    collector = ReadOutcomeCollector("example")
    module = SimpleNamespace(params={"state": "merged"})
    device = SimpleNamespace(get=lambda command: command + "\n")
    get_scoped_config(module, device, None, None, [DETAIL_COMMAND],
                      outcomes=collector, selectors={DETAIL_COMMAND: [("config", "1/1/1/1")]})
    assert collector.to_result()["outcomes"][0]["existence"] == "unknown"


@pytest.mark.parametrize("facts_path, cls, resource, config, command", [
    ("bridges.bridges", "BridgesFacts", "isam_bridges", {"port": [{"port": "1/1/5/1/4/1/1"}]},
     "info configure bridge port 1/1/5/1/4/1/1 flat detail"),
    ("qos_interfaces.qos_interfaces", "Qos_interfacesFacts", "isam_qos_interfaces", [{"name": "1/1/5/1/4/1/1"}],
     "info configure qos interface 1/1/5/1/4/1/1 flat"),
])
def test_bridges_and_qos_interfaces_record_targeted_outcomes(facts_path, cls, resource, config, command):
    # Header only (DS-LIN-TEST-01 2026-11-27, missing ONT 1/1/5/1/4): confirmed absent.
    import importlib
    facts = getattr(importlib.import_module(
        "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts." + facts_path), cls)
    sent = []

    def get(cmd):
        sent.append(cmd)
        return cmd + "\n#----------------\n"
    module = SimpleNamespace(params={"state": "gathered", "config": config})
    facts(module).get_config(SimpleNamespace(get=get))
    assert sent[0] == command
    outcomes = module._isam_read_outcomes["outcomes"]
    assert [(o["selector"], o["existence"]) for o in outcomes] == [("1/1/5/1/4/1/1", "confirmed_absent")]


def test_an_unobservable_setting_ignores_does_not_exist_on_the_first_read():
    # dhcp-relay answers the same set or not; the explicit error on the plain read
    # proves nothing either (review of #17).
    device = SimpleNamespace(get=lambda command: (_ for _ in ()).throw(Exception("Error : instance does not exist")))
    _, outcomes = read(device, unobservable_commands=(COMMAND,))
    assert outcomes["outcomes"][0]["existence"] == "unknown"

    class Replying(object):
        def get(self, command):
            return command + "\nError : instance does not exist\n"
    _, outcomes = read(Replying(), unobservable_commands=(COMMAND,))
    assert outcomes["outcomes"][0]["existence"] == "unknown"


def test_a_read_in_detail_flat_form_gets_no_second_probe_and_its_header_proves_absence():
    command = "info configure example interface 1/1/1/1 detail flat"
    sent = []

    def get(cmd):
        sent.append(cmd)
        return cmd + "\n#----------------\n"
    collector = ReadOutcomeCollector("example")
    module = SimpleNamespace(params={"state": "gathered"})
    get_scoped_config(module, SimpleNamespace(get=get), None, None, [command],
                      outcomes=collector, selectors={command: [("config", "1/1/1/1")]})
    assert sent == [command]
    assert collector.to_result()["outcomes"][0]["existence"] == "confirmed_absent"


@pytest.mark.parametrize("resource", ["epon_interfaces", "channel_pair_pm", "ngpon2_channel_groups"])
def test_a_rejected_pon_variant_single_read_is_never_confirmed_absent(resource):
    # The platform refuses the node ("invalid token"): only the whole read means "no
    # instances"; a targeted read is rejected / unknown (review of #17).
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.pon_variants.pon_variants import (
        VARIANT_COMMANDS, get_variant_config)
    full, single = VARIANT_COMMANDS[resource]

    def get(cmd):
        raise Exception("Error : invalid token")
    module = SimpleNamespace(params={"state": "gathered", "config": [{"name": "1/1/5/1", "id": "1"}]})
    get_variant_config(module, SimpleNamespace(get=get), resource)
    outcome = module._isam_read_outcomes["outcomes"][0]
    assert outcome["existence"] == "unknown" and outcome["command"] == "rejected"
    # The whole read on such a platform stays empty, as before.
    whole = SimpleNamespace(params={"state": "gathered", "config": None})
    assert get_variant_config(whole, SimpleNamespace(get=get), resource) == ""


def test_an_unobservable_section_keeps_the_dependency_gap_label():
    device = SimpleNamespace(get=lambda command: (_ for _ in ()).throw(Exception("Error : lower-interface does not exist")))
    _, outcomes = read(device, unobservable_commands=(COMMAND,))
    outcome = outcomes["outcomes"][0]
    assert outcome["existence"] == "unknown" and outcome.get("dependency_gap") == "lower-interface"


@pytest.mark.parametrize("reply", ["Error : lower-interface does not exist", "Error : The interface index cannot be calculated"])
def test_a_missing_dependency_on_the_detail_probe_keeps_its_label(reply):
    _, outcomes = read(Device(reply))
    outcome = outcomes["outcomes"][0]
    assert outcome["existence"] == "unknown" and outcome["command"] == "ok"
    assert outcome["dependency_gap"] in ("lower-interface", "interface-index")


def test_an_instance_check_of_another_section_keeps_this_commands_probe():
    # PAE ports and sftp users in one read: the sftp users' shared-node check must not
    # switch off the PAE port's detail probe (review note on #12).
    other = "info configure example shared flat"
    sent = []

    def get(cmd):
        sent.append(cmd)
        if cmd == COMMAND + " detail":
            return cmd + "\n" + PATH + " no enabled\n"
        return cmd + "\n#----------------\n"
    collector = ReadOutcomeCollector("example")
    module = SimpleNamespace(params={"state": "gathered"})
    get_scoped_config(module, SimpleNamespace(get=get), None, None, [COMMAND, other], outcomes=collector,
                      selectors={COMMAND: [("config", "1/1/1/1")], other: [("users", "u1")]},
                      instance_checks={("users", "u1"): lambda reply: "u1" in reply})
    assert COMMAND + " detail" in sent
    outcomes = dict((o["selector"], o["existence"]) for o in collector.to_result()["outcomes"])
    assert outcomes == {"1/1/1/1": "present", "u1": "unknown"}


def test_a_whole_node_read_honours_the_unobservable_policy(monkeypatch):
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam import targeted
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts import facts_base
    monkeypatch.setitem(targeted.ABSENCE_POLICY, "example_node", {"config": "unobservable"})
    monkeypatch.setitem(targeted.TARGETED_GATHER, "example_node", {"config": "name"})
    module = SimpleNamespace(params={"state": "gathered", "config": [{"name": "a"}]})

    def get(cmd):
        raise Exception("Error : instance does not exist")
    facts_base.get_whole_node_targeted(module, SimpleNamespace(get=get), "example_node",
                                       "info configure example flat", ["config"], lambda reply: [])
    assert module._isam_read_outcomes["outcomes"][0]["existence"] == "unknown"
