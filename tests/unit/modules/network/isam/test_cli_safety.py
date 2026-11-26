"""CLI command safety: no control character in a command leaves the collection.

A new line in a module value would end the command and inject a second CLI line
(e.g. ``admin equipment reboot-isam``), even in read-only ``gathered``. The check is
central: resource modules (every state that shows or sends commands), targeted reads,
and the cliconf plugin as a backstop. Messages name positions, never command text
(commands may carry passwords).
"""
import json

import pytest

from ansible_collections.nokia.isam.plugins.cliconf.isam import Cliconf
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.cli_safety import (
    UnsafeCliCommandError,
    check_cli_commands,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    targeted_commands,
)

from .module_runner import run_module
from .targeted_harness import Device, gathered

INJECT = "x\nadmin equipment reboot-isam with-self-test"
SAFE_VALUES = [
    "two words",
    'say "hi"',
    "a:b/c.d_e-f",
    "Grüße ñandú",
    "#hash",
]


# -- the helper ---------------------------------------------------------------

@pytest.mark.parametrize("char", ["\n", "\r", "\t", "\x00", "\x03", "\x15", "\x1b", "\x1f", "\x7f"])
def test_every_control_character_is_rejected(char):
    with pytest.raises(UnsafeCliCommandError) as raised:
        check_cli_commands(["configure system id 1", "configure vlan id 1 name a%sb" % char], "test")
    assert "#2 of 2" in str(raised.value)
    assert "vlan" not in str(raised.value)  # no command text


def test_bytes_commands_are_checked():
    with pytest.raises(UnsafeCliCommandError):
        check_cli_commands([b"info configure\nadmin"], "test")
    assert check_cli_commands([b"info configure flat"], "test") == [b"info configure flat"]


@pytest.mark.parametrize("value", SAFE_VALUES)
def test_printable_values_pass(value):
    command = 'configure vlan id 1 name "%s"' % value
    assert check_cli_commands([command], "test") == [command]


def test_message_never_contains_a_secret():
    with pytest.raises(UnsafeCliCommandError) as raised:
        check_cli_commands(["configure system security operator op password plain:S3cret\nx"], "test")
    assert "S3cret" not in str(raised.value)
    assert "operator" not in str(raised.value)


# -- (a) resource modules ---------------------------------------------------------

def _assert_refused(result, *hidden):
    assert result.get("failed"), result
    assert "control character" in result["msg"]
    assert not result.get("rendered") and not result.get("commands"), result
    for text in hidden:
        assert text not in result["msg"]
    assert not any("reboot-isam" in command for command in result.get("_sent", []))


def test_rendered_vlan_name_with_new_line_fails_without_emitting(monkeypatch):
    result = run_module(monkeypatch, "isam_vlans", {
        "state": "rendered", "config": [{"id": 100, "mode": "residential-bridge", "name": INJECT}]})
    _assert_refused(result, "reboot-isam")


def test_rendered_operator_with_new_line_fails_and_hides_password(monkeypatch):
    result = run_module(monkeypatch, "isam_system_security", {
        "state": "rendered", "config": {"operators": [
            {"name": INJECT, "password": "plain:Sup3rSecret", "profile": "admin"}]}})
    _assert_refused(result, "reboot-isam", "Sup3rSecret")


def test_offline_render_with_new_line_fails(monkeypatch):
    # deleted + canonical running_config: the offline removal preview
    result = run_module(monkeypatch, "isam_system_security", {
        "state": "deleted", "running_config": json.dumps({"operators": [{"name": INJECT, "profile": "admin"}]})})
    _assert_refused(result, "reboot-isam")


def test_merged_against_device_with_new_line_fails_before_sending(monkeypatch):
    result = run_module(monkeypatch, "isam_vlans", {
        "state": "merged", "config": [{"id": 100, "mode": "residential-bridge", "name": INJECT}]})
    _assert_refused(result, "reboot-isam")


@pytest.mark.parametrize("value", SAFE_VALUES)
def test_rendered_printable_values_still_pass(monkeypatch, value):
    result = run_module(monkeypatch, "isam_vlans", {
        "state": "rendered", "config": [{"id": 100, "mode": "residential-bridge", "name": value}]})
    assert not result.get("failed"), result
    assert len(result["rendered"]) == 1 and result["rendered"][0].startswith("configure vlan id 100 ")


# -- (b) targeted reads -------------------------------------------------------------

def test_targeted_gathered_with_new_line_identity_sends_nothing(monkeypatch):
    case = {"module": "isam_system_security"}
    device = Device(["configure system security operator isadmin profile admin"])
    result = gathered(monkeypatch, case, {"operators": [{"name": "isadmin flat\nadmin equipment reboot-isam"}]},
                      device)
    assert result.get("failed"), result
    assert "control character" in result["msg"] and "reboot-isam" not in result["msg"]
    assert device.commands == []


def test_targeted_gathered_with_safe_identity_still_reads(monkeypatch):
    case = {"module": "isam_system_security"}
    device = Device(["configure system security operator isadmin profile admin"])
    result = gathered(monkeypatch, case, {"operators": [{"name": "isadmin"}]}, device)
    assert not result.get("failed"), result
    assert device.commands and all("\n" not in command for command in device.commands)


def test_targeted_commands_rejects_new_line_identity():
    class Module(object):
        params = {"state": "gathered", "config": [{"id": "10 flat\nadmin equipment reboot-isam"}]}

    with pytest.raises(UnsafeCliCommandError):
        targeted_commands(Module(), "vlans", {"config": "info configure vlan id %s flat"})


# -- (c) cliconf backstop ---------------------------------------------------------------

def _cliconf():
    plugin = object.__new__(Cliconf)
    plugin._device_info = {}
    plugin.sent = []

    def send_command(command=None, *a, **k):
        plugin.sent.append(command)
        return "ok"

    plugin.send_command = send_command
    plugin.get_device_operations = lambda *a, **k: {}
    plugin.check_edit_config_capability = lambda *a, **k: None
    return plugin


def test_cliconf_edit_config_refuses_whole_candidate_before_writing():
    plugin = _cliconf()
    with pytest.raises(UnsafeCliCommandError):
        plugin.edit_config(candidate=["configure system id 1", 'configure vlan id 1 name "%s"' % INJECT])
    assert plugin.sent == []


def test_cliconf_get_refuses_new_line():
    plugin = _cliconf()
    with pytest.raises(UnsafeCliCommandError):
        plugin.get("info configure vlan id 10 flat\nadmin equipment reboot-isam")
    assert plugin.sent == []


def test_cliconf_send_command_refuses_new_line_before_the_channel(monkeypatch):
    from ansible.plugins.cliconf import CliconfBase

    written = []
    monkeypatch.setattr(CliconfBase, "send_command", lambda self, command=None, *a, **k: written.append(command))
    plugin = object.__new__(Cliconf)
    with pytest.raises(UnsafeCliCommandError):
        plugin.send_command("show equipment slot\r\nadmin equipment reboot-isam")
    plugin.send_command("show equipment slot")
    assert written == ["show equipment slot"]


@pytest.mark.parametrize("value", SAFE_VALUES)
def test_cliconf_printable_values_pass(value):
    plugin = _cliconf()
    command = 'configure vlan id 1 name "%s"' % value
    plugin.edit_config(candidate=[command])
    assert plugin.get("info configure vlan id 1 flat") == "ok"
    assert plugin.sent == ["exit all", command, "info configure vlan id 1 flat"]


def _inject(config):
    """config with a new line appended to every string value in each instance list."""
    if isinstance(config, list):
        return [_inject(item) for item in config]
    if isinstance(config, dict):
        return dict((key, value + "\nadmin equipment reboot-isam" if isinstance(value, str) else _inject(value))
                    for key, value in config.items())
    return config


def _targeted_cases():
    from .test_targeted_gathered import CASES

    return CASES


@pytest.mark.parametrize("name", sorted(_targeted_cases()))
def test_no_targeted_family_sends_a_control_character(monkeypatch, name):
    case = _targeted_cases()[name]
    config = _inject(case["config"])
    device = Device(case["lines"] + case["sibling"], answer=case.get("answer"))
    try:
        result = gathered(monkeypatch, case, config, device)
    except Exception:  # argspec type conversion etc. -- what matters is the channel
        result = {}
    assert not any(check_unsafe(command) for command in device.commands), device.commands
    if config != case["config"] and not device.commands:
        assert result.get("failed"), result


def check_unsafe(command):
    try:
        check_cli_commands([command], "test")
    except UnsafeCliCommandError:
        return True
    return False
