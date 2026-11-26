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
