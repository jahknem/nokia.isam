"""Write states of the L2CP resources compare against the device (they used to compare against nothing)."""
from ansible.module_utils import basic
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from ansible_collections.nokia.isam.plugins.modules import isam_l2cp, isam_l2cp_session, isam_l2cp_user_port
from .isam_module import TestIsamModule, set_module_args

FACTS = "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.%s.%s.get_resource_connection"


class _Device(object):
    """Answers the whole-resource read; any other read is a device error."""

    def __init__(self, outputs):
        self.outputs, self.commands = outputs, []

    def get(self, command, *args, **kwargs):
        self.commands.append(command)
        if command not in self.outputs:
            raise Exception("Error : invalid token")
        return self.outputs[command]


SESSIONS = (
    "configure l2cp session 1 bras-ip-address 192.0.2.10 alive-timer 300 sig-partition-id\n"
    "configure l2cp session 2 bras-ip-address 192.0.2.20\n"
)
USER_PORTS = (
    "configure l2cp user-port 1/1/1/1 partition-id 7\n"
    "configure l2cp user-port 1/1/1/2 partition-id 8\n"
)


class _Base(TestIsamModule):
    resource = None
    read = None
    output = ""

    def commands(self, state, config=None, expected=(), output=None):
        """Run state in check mode against a device holding output; assert the exact commands."""
        device = _Device({self.read: self.output if output is None else output})
        patcher = patch(FACTS % (self.resource, self.resource), return_value=device)
        patcher.start()
        self.addCleanup(patcher.stop)
        args = {"state": state, "_ansible_check_mode": True}
        if config is not None:
            args["config"] = config
        set_module_args(args, True)
        result = self.execute_module(changed=bool(expected))
        self.assertIn(self.read, device.commands)
        self.assertEqual(result["commands"], list(expected))
        return result


class TestL2cpWrites(_Base):
    module = isam_l2cp
    resource = "l2cp"
    read = "info configure l2cp flat"
    output = "configure l2cp partition-type fixed-assigned\n"

    def test_merged_is_idempotent(self):
        self.commands("merged", [{"name": "l2cp", "partition_type": "fixed-assigned"}])

    def test_merged_changes(self):
        self.commands("merged", [{"name": "l2cp", "partition_type": "fixed-assigned"}], [
            "configure l2cp partition-type fixed-assigned"], output="")

    def test_default_on_unconfigured_device_is_idempotent(self):
        # used to send "configure l2cp no partition-type" on every run
        for state in ("merged", "replaced", "overridden"):
            self.commands(state, [{"name": "l2cp"}], output="")

    def test_replaced_resets(self):
        self.commands("replaced", [{"name": "l2cp", "partition_type": "no-partition"}], ["configure l2cp no partition-type"])

    def test_deleted(self):
        self.commands("deleted", None, ["configure l2cp no partition-type"])
        self.commands("deleted", [{"name": "l2cp"}], ["configure l2cp no partition-type"])

    def test_deleted_is_idempotent_when_l2cp_is_unconfigured(self):
        self.commands("deleted", [{"name": "l2cp"}], output="")

    def test_device_error_fails(self):
        device = _Device({})
        patcher = patch(FACTS % ("l2cp", "l2cp"), return_value=device)
        patcher.start()
        self.addCleanup(patcher.stop)
        set_module_args({"state": "deleted", "_ansible_check_mode": True}, True)
        result = self.execute_module(failed=True)
        self.assertIn("invalid token", result["msg"])


class TestL2cpSessionWrites(_Base):
    module = isam_l2cp_session
    resource = "l2cp_session"
    read = "info configure l2cp session flat"
    output = SESSIONS

    def test_merged_is_idempotent(self):
        self.commands("merged", [
            {"name": "1", "bras_ip_address": "192.0.2.10", "alive_timer": "300", "sig_partition_id": True},
            {"name": "2", "bras_ip_address": "192.0.2.20"},
        ])

    def test_merged_changes_only_the_differing_session(self):
        # An existing session takes only the short form (lab ISAM: repeating bras-ip-address is refused).
        self.commands("merged", [
            {"name": "1", "bras_ip_address": "192.0.2.10", "alive_timer": "300", "sig_partition_id": True},
            {"name": "2", "bras_ip_address": "192.0.2.20", "alive_timer": "200"},
        ], ["configure l2cp session 2 alive-timer 200"])

    def test_merged_keeps_bras_address_of_existing_session(self):
        self.commands("merged", [{"name": "2", "tcp_retry_time": "20"}], ["configure l2cp session 2 tcp-retry-time 20"])

    def test_merged_without_bras_address_cannot_create(self):
        with patch.object(basic.AnsibleModule, "warn") as warn:
            self.commands("merged", [{"name": "9"}])
        self.assertIn("bras_ip_address", warn.call_args[0][0])

    def test_replaced_negates_unnamed_attributes(self):
        self.commands("replaced", [{"name": "1", "bras_ip_address": "192.0.2.10", "sig_partition_id": True}], [
            "configure l2cp session 1 no alive-timer"])

    def test_overridden_removes_unnamed_sessions(self):
        self.commands("overridden", [{"name": "2", "bras_ip_address": "192.0.2.20"}], ["configure l2cp no session 1"])

    def test_gathered_with_config_sends_nothing(self):
        device = _Device({self.read: SESSIONS, "info configure l2cp session 9 flat": ""})
        patcher = patch(FACTS % (self.resource, self.resource), return_value=device)
        patcher.start()
        self.addCleanup(patcher.stop)
        set_module_args({"state": "gathered", "config": [{"name": "9", "bras_ip_address": "192.0.2.9"}]}, True)
        result = self.execute_module(changed=False)
        self.assertNotIn("commands", result)
        self.assertEqual(device.commands, ["info configure l2cp session 9 flat"])

    def test_deleted_named_and_all(self):
        self.commands("deleted", [{"name": "2"}, {"name": "9"}], ["configure l2cp no session 2"])
        self.commands("deleted", None, ["configure l2cp no session 1", "configure l2cp no session 2"])
        self.commands("deleted", None, output="")


class TestL2cpUserPortWrites(_Base):
    module = isam_l2cp_user_port
    resource = "l2cp_user_port"
    read = "info configure l2cp user-port flat"
    output = USER_PORTS

    def test_merged_is_idempotent(self):
        self.commands("merged", [{"name": "1/1/1/1", "partition_id": "7"}, {"name": "1/1/1/2", "partition_id": "8"}])

    def test_merged_adds(self):
        self.commands("merged", [{"name": "1/1/1/3", "partition_id": "9"}], ["configure l2cp user-port 1/1/1/3 partition-id 9"])

    def test_replaced_moves_partition(self):
        # the removal form needs the assigned partition id (CLI identity: user-port + partition-id)
        self.commands("replaced", [{"name": "1/1/1/1", "partition_id": "9"}], [
            "configure l2cp no user-port 1/1/1/1 partition-id 7",
            "configure l2cp user-port 1/1/1/1 partition-id 9",
        ])
        self.commands("replaced", [{"name": "1/1/1/1", "partition_id": "7"}])

    def test_overridden_removes_unnamed_ports(self):
        self.commands("overridden", [{"name": "1/1/1/1", "partition_id": "7"}], [
            "configure l2cp no user-port 1/1/1/2 partition-id 8"])

    def test_deleted_named_and_all(self):
        self.commands("deleted", [{"name": "1/1/1/2"}], ["configure l2cp no user-port 1/1/1/2 partition-id 8"])
        self.commands("deleted", None, [
            "configure l2cp no user-port 1/1/1/1 partition-id 7",
            "configure l2cp no user-port 1/1/1/2 partition-id 8",
        ])
        self.commands("deleted", [{"name": "1/1/1/9"}])


def test_rendered_never_turns_a_partial_entry_into_a_removal(monkeypatch):
    """A session needs bras_ip_address and an assignment its partition_id to be created;
    rendered fails naming the missing field instead of rendering the removal form."""
    from .module_runner import run_module

    result = run_module(monkeypatch, "isam_l2cp_session", {"state": "rendered", "config": [{"name": "1", "alive_timer": "300"}]})
    assert result.get("failed") and "bras_ip_address is mandatory" in result["msg"]
    result = run_module(monkeypatch, "isam_l2cp_user_port", {"state": "rendered", "config": [{"name": "1/1/1/1"}]})
    assert result.get("failed") and "partition_id is mandatory" in result["msg"]
    assert run_module(monkeypatch, "isam_l2cp", {"state": "rendered", "config": [{"name": "l2cp"}]})["rendered"] == []
    # complete entries render their creation commands
    assert run_module(monkeypatch, "isam_l2cp_session", {"state": "rendered", "config": [
        {"name": "1", "bras_ip_address": "192.0.2.10", "alive_timer": "300"}]})["rendered"] == [
        "configure l2cp session 1 bras-ip-address 192.0.2.10 alive-timer 300"]
    assert run_module(monkeypatch, "isam_l2cp_user_port", {"state": "rendered", "config": [
        {"name": "1/1/1/1", "partition_id": "7"}]})["rendered"] == ["configure l2cp user-port 1/1/1/1 partition-id 7"]


def test_l2cp_families_use_the_common_lifecycle():
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.l2cp.l2cp import L2cp
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.l2cp_session.l2cp_session import L2cpSession
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.l2cp_user_port.l2cp_user_port import L2cpUserPort
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule

    for cls in (L2cp, L2cpSession, L2cpUserPort):
        assert cls.execute_module is IsamResourceModule.execute_module, cls
