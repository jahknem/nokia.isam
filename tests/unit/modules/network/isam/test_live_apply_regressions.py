"""Sanitized, offline regressions for the 2026-11-19 live-apply handover."""
import json

import pytest

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base import resource_module_base
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts import facts
from ansible_collections.nokia.isam.plugins.modules import isam_bridges, isam_equipment_onts, isam_interfaces, isam_qos_interfaces
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.equipment_onts import equipment_onts

from .isam_module import set_module_args


class Connection:
    def __init__(self, running=""):
        self.running = running
        self.reads = []
        self.writes = []

    def get(self, command):
        self.reads.append(command)
        return self.running

    def edit_config(self, candidate):
        self.writes.append(list(candidate))
        return {"response": [""] * len(candidate)}


def invoke(monkeypatch, capsys, module, config, state, running="", check_mode=True, connection=None, expected_rc=0):
    connection = connection or Connection(running)
    monkeypatch.setattr(resource_module_base, "get_resource_connection", lambda module: connection)
    monkeypatch.setattr(facts, "get_resource_connection", lambda module: connection)
    set_module_args({"state": state, "config": config, "_ansible_check_mode": check_mode}, True)
    with pytest.raises(SystemExit) as exited:
        module.main()
    result = json.loads(capsys.readouterr().out)
    assert exited.value.code == expected_rc, result
    return result, connection


@pytest.mark.parametrize("state", ["merged", "rendered"])
def test_slot_creation_keeps_admin_state_standalone(monkeypatch, capsys, state):
    config = {"interfaces": [{"ont_idx": "1/1/6/1/1", "sw_ver_pland": "auto", "admin_state": "up"}],
              "slots": [{"ont_slot_idx": "1/1/6/1/1/1", "planned_card_type": "ethernet",
                         "plndnumdataports": 1, "admin_state": "up"}]}
    result, connection = invoke(monkeypatch, capsys, isam_equipment_onts, config, state)
    assert result.get("rendered", result.get("commands")) == [
        "configure equipment ont interface 1/1/6/1/1 sw-ver-pland auto",
        "configure equipment ont interface 1/1/6/1/1 admin-state up",
        "configure equipment ont slot 1/1/6/1/1/1 planned-card-type ethernet plndnumdataports 1",
        "configure equipment ont slot 1/1/6/1/1/1 admin-state up",
    ]
    assert connection.writes == []


@pytest.mark.parametrize("state", ["merged", "rendered"])
def test_admin_only_slot_request_does_not_add_a_bare_creation_command(monkeypatch, capsys, state):
    result, _ = invoke(monkeypatch, capsys, isam_equipment_onts,
                       {"slots": [{"ont_slot_idx": "1/1/6/1/1/1", "admin_state": "up"}]}, state)
    assert result.get("rendered", result.get("commands")) == [
        "configure equipment ont slot 1/1/6/1/1/1 admin-state up"]


@pytest.mark.parametrize("state", ["replaced", "overridden"])
def test_admin_state_resets_are_standalone_too(monkeypatch, capsys, state):
    running = ("configure equipment ont interface 1/1/6/1/1 sw-ver-pland auto desc1 Example admin-state up\n"
               "configure equipment ont slot 1/1/6/1/1/1 planned-card-type ethernet plndnumdataports 1 admin-state up\n")
    config = {"interfaces": [{"ont_idx": "1/1/6/1/1", "sw_ver_pland": "auto"}],
              "slots": [{"ont_slot_idx": "1/1/6/1/1/1", "planned_card_type": "ethernet"}]}
    result, _ = invoke(monkeypatch, capsys, isam_equipment_onts, config, state, running)
    assert result["commands"] == [
        "configure equipment ont interface 1/1/6/1/1 no desc1",
        "configure equipment ont interface 1/1/6/1/1 no admin-state",
        "configure equipment ont slot 1/1/6/1/1/1 no plndnumdataports",
        "configure equipment ont slot 1/1/6/1/1/1 no admin-state",
    ]


def test_delete_already_down_interface_and_slot_reasserts_shutdown(monkeypatch, capsys):
    config = {"interfaces": [{"ont_idx": "1/1/6/1/1"}], "slots": [{"ont_slot_idx": "1/1/6/1/1/1"}]}
    running = ("configure equipment ont interface 1/1/6/1/1 admin-state down\n"
               "configure equipment ont slot 1/1/6/1/1/1 planned-card-type ethernet admin-state down\n")
    result, connection = invoke(monkeypatch, capsys, isam_equipment_onts, config, "deleted", running)
    assert result["commands"] == [
        "configure equipment ont interface 1/1/6/1/1 admin-state down",
        "configure equipment ont slot 1/1/6/1/1/1 admin-state down",
        "configure equipment ont no slot 1/1/6/1/1/1",
        "configure equipment ont no interface 1/1/6/1/1",
    ]
    assert connection.writes == []


@pytest.mark.parametrize("state", ["merged", "replaced", "overridden", "deleted", "rendered"])
def test_severity_no_value_is_never_sent_as_a_value(monkeypatch, capsys, state):
    name = "vlan-port:1/1/6/1/1/1/1:99"
    config = [{"name": name, "severity": "no-value"}]
    running = "configure interface port %s severity no-value\n" % name
    result, _ = invoke(monkeypatch, capsys, isam_interfaces, config, state, running)
    commands = result.get("rendered", result.get("commands"))
    assert commands == (["configure interface port %s no severity" % name] if state == "rendered" else [])


@pytest.mark.parametrize("state", ["replaced", "overridden", "deleted"])
def test_qos_identity_only_does_not_reset_unsupported_detail_defaults(monkeypatch, capsys, state):
    name = "vlan:1/1/6/1/1/1/1:99"
    running = "\n".join("configure qos interface %s %s" % (name, attr) for attr in (
        "ds-num-queue not-applicable", "bc-scheduler-node none", "mc-scheduler-node not-applicable",
        "upstream-queue 0 bandwidth-profile none", "upstream-queue 0 queue-profile not-applicable"))
    result, _ = invoke(monkeypatch, capsys, isam_qos_interfaces, [{"name": name}], state, running)
    assert result["commands"] == []


@pytest.mark.parametrize("state", ["merged", "rendered"])
def test_qos_replay_drops_not_applicable_but_keeps_real_queue_profile(monkeypatch, capsys, state):
    name = "vlan:1/1/6/1/1/1/1:99"
    config = [{"name": name, "ds_num_queue": "not-applicable", "bc_scheduler_node": "none",
               "upstream_queue": [{"id": 0, "bandwidth_profile": "name:TEST_UP",
                                   "queue_profile": "not-applicable"}]}]
    result, _ = invoke(monkeypatch, capsys, isam_qos_interfaces, config, state)
    assert result.get("rendered", result.get("commands")) == [
        "configure qos interface %s upstream-queue 0 bandwidth-profile name:TEST_UP" % name]


def test_explicit_none_still_clears_a_configured_qos_profile(monkeypatch, capsys):
    name = "pon:1/1/6/1"
    result, _ = invoke(monkeypatch, capsys, isam_qos_interfaces,
                       [{"name": name, "cac_profile": "none"}], "merged",
                       "configure qos interface %s cac-profile name:TEST_CAC" % name)
    assert result["commands"] == ["configure qos interface %s cac-profile none" % name]


@pytest.mark.parametrize("state", ["merged", "replaced"])
def test_severity_no_value_resets_a_real_severity(monkeypatch, capsys, state):
    name = "vlan-port:1/1/6/1/1/1/1:99"
    result, _ = invoke(monkeypatch, capsys, isam_interfaces, [{"name": name, "severity": "no-value"}], state,
                       "configure interface port %s severity major\n" % name)
    assert result["commands"] == ["configure interface port %s no severity" % name]


SHUTDOWNS = ["configure equipment ont interface 1/1/6/1/1 admin-state down",
             "configure equipment ont slot 1/1/6/1/1/1 admin-state down"]
REMOVALS = ["configure equipment ont no slot 1/1/6/1/1/1", "configure equipment ont no interface 1/1/6/1/1"]
DELETE_CONFIG = {"interfaces": [{"ont_idx": "1/1/6/1/1"}], "slots": [{"ont_slot_idx": "1/1/6/1/1/1"}]}


class ShutdownConnection(Connection):
    """Delayed shutdown/readback, with independently failing reads and writes."""
    def __init__(self, ready_after=2, read_error=False, fail_command=None):
        super().__init__("\n".join(SHUTDOWNS).replace("admin-state down", "admin-state up"))
        self.ready_after = ready_after
        self.read_error = read_error
        self.fail_command = fail_command
        self.polls = {}
        self.events = []

    def get(self, command):
        self.events.append(("read", command))
        if not self.writes:
            return super().get(command)
        if self.read_error:
            raise RuntimeError("readback unavailable")
        self.polls[command] = self.polls.get(command, 0) + 1
        path = command.removeprefix("info ").removesuffix(" flat detail")
        state = "down" if self.polls[command] >= self.ready_after else "up"
        return path + " admin-state " + state

    def edit_config(self, candidate):
        self.events.append(("write", list(candidate)))
        response = super().edit_config(candidate)
        if self.fail_command in candidate:
            raise RuntimeError("device refused command")
        return response


def stage_delete(monkeypatch, capsys, connection, expected_rc=0):
    monkeypatch.setattr(equipment_onts.time, "sleep", lambda seconds: connection.events.append(("sleep", seconds)))
    return invoke(monkeypatch, capsys, isam_equipment_onts, DELETE_CONFIG, "deleted",
                  check_mode=False, connection=connection, expected_rc=expected_rc)[0]


def test_delete_waits_for_interface_and_slot_before_any_removal(monkeypatch, capsys):
    connection = ShutdownConnection()
    result = stage_delete(monkeypatch, capsys, connection)
    assert result["commands"] == SHUTDOWNS + REMOVALS
    assert connection.writes == [[command] for command in SHUTDOWNS + REMOVALS]
    # Two readiness polls per object, then the resource's normal after-facts read.
    assert list(connection.polls.values()) == [3, 3]
    assert sum(event[0] == "sleep" for event in connection.events) == 2
    first_removal = connection.events.index(("write", [REMOVALS[0]]))
    assert sum(event[0] == "read" for event in connection.events[:first_removal]) == 6


@pytest.mark.parametrize("read_error", [False, True])
def test_shutdown_timeout_or_read_failure_never_sends_removals(monkeypatch, capsys, read_error):
    connection = ShutdownConnection(ready_after=100, read_error=read_error)
    result = stage_delete(monkeypatch, capsys, connection, expected_rc=1)
    assert result["changed"] is True and result["failed"] is True
    assert result["failure_phase"] == "shutdown_verification"
    assert result["accepted"] == SHUTDOWNS
    assert result["pending"] == REMOVALS
    assert result["failed_command"] is None
    assert connection.writes == [[command] for command in SHUTDOWNS]
    if not read_error:
        assert list(connection.polls.values()) == [equipment_onts.Equipment_onts.SHUTDOWN_VERIFY_ATTEMPTS] * 2


@pytest.mark.parametrize("failed_index", [0, 1, 2, 3])
def test_staged_delete_write_failures_report_partial_progress_without_retry(monkeypatch, capsys, failed_index):
    commands = SHUTDOWNS + REMOVALS
    connection = ShutdownConnection(ready_after=1, fail_command=commands[failed_index])
    result = stage_delete(monkeypatch, capsys, connection, expected_rc=1)
    assert result["failure_phase"] == "execution"
    assert result["changed"] is True
    assert result["accepted"] == commands[:failed_index]
    assert result["failed_command"] == commands[failed_index]
    assert result["pending"] == commands[failed_index + 1:]
    assert connection.writes == [[command] for command in commands[:failed_index + 1]]


def test_check_mode_does_not_wait_or_write_for_shutdown(monkeypatch, capsys):
    monkeypatch.setattr(equipment_onts.time, "sleep", lambda seconds: pytest.fail("check mode must not wait"))
    result, connection = invoke(monkeypatch, capsys, isam_equipment_onts, DELETE_CONFIG, "deleted",
                                "\n".join(SHUTDOWNS))
    assert result["commands"] == SHUTDOWNS + REMOVALS
    assert connection.writes == []


def test_named_field_deletion_does_not_shutdown_or_remove_ont(monkeypatch, capsys):
    monkeypatch.setattr(equipment_onts.time, "sleep", lambda seconds: pytest.fail("no shutdown needed"))
    result, connection = invoke(monkeypatch, capsys, isam_equipment_onts,
                                {"interfaces": [{"ont_idx": "1/1/6/1/1", "desc1": "Example"}]}, "deleted",
                                "configure equipment ont interface 1/1/6/1/1 desc1 Example admin-state up\n",
                                check_mode=False)
    assert result["commands"] == ["configure equipment ont interface 1/1/6/1/1 no desc1"]
    assert connection.writes == [result["commands"]]


@pytest.mark.parametrize("state", ["merged", "replaced", "rendered"])
def test_severity_no_value_is_not_replayed_onto_a_new_target(monkeypatch, capsys, state):
    name = "vlan-port:1/1/6/1/1/1/1:99"
    result, _ = invoke(monkeypatch, capsys, isam_interfaces,
                       [{"name": name, "severity": "no-value", "admin_up": True}], state)
    expected = "configure interface port %s %s" % (name, "admin-up no severity" if state == "rendered" else "admin-up")
    assert result.get("rendered", result.get("commands")) == [expected]


@pytest.mark.parametrize("reply", ["", "# empty detail", "configure equipment ont interface 1/1/6/1/2 admin-state down"])
def test_missing_or_wrong_identity_shutdown_readback_is_not_confirmation(monkeypatch, capsys, reply):
    connection = ShutdownConnection()
    original_get = connection.get

    def get(command):
        return reply if connection.writes else original_get(command)

    monkeypatch.setattr(connection, "get", get)
    result = stage_delete(monkeypatch, capsys, connection, expected_rc=1)
    assert result["pending"] == REMOVALS
    assert result["accepted"] == SHUTDOWNS
    assert connection.writes == [[command] for command in SHUTDOWNS]


@pytest.mark.parametrize("state", ["merged", "replaced"])
def test_unsupported_qos_placeholder_does_not_erase_a_real_target_binding(monkeypatch, capsys, state):
    name = "vlan:1/1/6/1/1/1/1:99"
    result, _ = invoke(monkeypatch, capsys, isam_qos_interfaces,
                       [{"name": name, "bc_scheduler_node": "not-applicable"}], state,
                       "configure qos interface %s bc-scheduler-node name:TEST_BC\n" % name)
    assert result["commands"] == []


def test_caller_provisions_upstream_bandwidth_before_bridge_vlan_attachment(monkeypatch, capsys):
    """Cross-resource prerequisite belongs to the caller, not implicit bridge writes."""
    name = "1/1/6/1/1/1/1"

    class DependencyConnection(Connection):
        profile_ready = False

        def edit_config(self, candidate):
            for command in candidate:
                if command == "configure qos interface %s upstream-queue 0 bandwidth-profile name:TEST_UP" % name:
                    self.profile_ready = True
                if command.startswith("configure bridge port ") and " vlan-id " in command:
                    assert self.profile_ready, "missing bandwidth profile on queue (VLAN MGT error 277)"
            return super().edit_config(candidate)

    connection = DependencyConnection()
    qos, _ = invoke(monkeypatch, capsys, isam_qos_interfaces,
                     [{"name": name, "upstream_queue": [{"id": 0, "bandwidth_profile": "name:TEST_UP"}]}],
                     "merged", connection=connection, check_mode=False)
    bridge, _ = invoke(monkeypatch, capsys, isam_bridges,
                        {"port": [{"port": name, "pvid": 99, "vlan_id": [{"id": 99}]}]},
                        "merged", connection=connection, check_mode=False)
    assert qos["changed"] and bridge["changed"]
    assert connection.writes == [qos["commands"], bridge["commands"]]
    assert all(not command.startswith("configure qos ") for command in bridge["commands"])
    assert bridge["commands"].index("configure bridge port %s vlan-id 99" % name) < bridge["commands"].index(
        "configure bridge port %s pvid 99" % name)
