import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.action_module import IsamActionModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.security_ext_authenticator.security_ext_authenticator import (
    Isam_security_ext_authenticator,
)
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

CONNECTION = "ansible_collections.nokia.isam.plugins.module_utils.network.isam.action_module.get_resource_connection"


class FakeFail(Exception):
    def __init__(self, kwargs):
        self.kwargs = kwargs
        super(FakeFail, self).__init__(kwargs.get("msg", ""))


class FakeModule:
    def __init__(self, config, check_mode=True):
        self.params = {"config": config}
        self.check_mode = check_mode
        self.warnings = []

    def fail_json(self, **kwargs):
        raise FakeFail(kwargs)

    def warn(self, msg):
        self.warnings.append(msg)


class FakeConnection:
    """edit_config is called once per command (single-command transactions)."""

    def __init__(self, responses=None, fail_on=None, error=None, malformed=False):
        self.calls = []
        self._responses = responses or {}
        self._fail_on = fail_on
        self._error = error or RuntimeError("device refused")
        self._malformed = malformed

    def edit_config(self, candidate):
        self.calls.append(list(candidate))
        command = candidate[0]
        if self._fail_on is not None and command == self._fail_on:
            raise self._error
        if self._malformed:
            return None
        return {"request": list(candidate), "response": self._responses.get(command, ["ok"])}


def _module(config, check_mode=True):
    return Isam_security_ext_authenticator(FakeModule(config, check_mode))


def _cmd(port):
    return "admin security ext-authenticator %s clear-statistics" % port


# --- the operation is required: a bare resource path only navigates, it is not an action ---

def test_clear_statistics_is_required():
    for config in ([{"port": "1/1/1/1"}], [{"port": "1/1/1/1", "clear_statistics": False}]):
        with pytest.raises(FakeFail) as exc:
            _module(config).build_commands()
        assert "explicit operation" in exc.value.kwargs["msg"]


def test_one_entry_without_operation_fails_the_whole():
    with pytest.raises(FakeFail):
        _module([{"port": "1/1/1/1", "clear_statistics": True}, {"port": "1/1/1/2"}]).build_commands()


# --- identifier validation (P2): no whitespace, control characters or separators ---

@pytest.mark.parametrize("port", [
    "1/1/1/1 extra", "1/1/1/1\nadmin equipment slot 1 reboot", "1/1/1/1;reboot",
    "1/1/1/1\t", "", "1/1/1/1\x00", "1/1/1/1|foo", "1/1/1/1 && x",
])
def test_invalid_port_identifiers_rejected(port):
    with pytest.raises(FakeFail) as exc:
        _module([{"port": port, "clear_statistics": True}]).build_commands()
    assert "Invalid port" in exc.value.kwargs["msg"]


@pytest.mark.parametrize("port", [
    "1/1/1/1", "1/1/1/1:100:200", "1/1/1/1/1/1", "1/1/1/1/voip", "ng2:1/1/1/1/1/1", "lt:1/1/6",
])
def test_valid_port_formats_accepted(port):
    assert _module([{"port": port, "clear_statistics": True}]).build_commands() == [_cmd(port)]


def test_validate_identifier_helper():
    action = IsamActionModule(FakeModule([]))
    assert action.validate_identifier("1/1/1/1", "port") == "1/1/1/1"
    with pytest.raises(FakeFail):
        action.validate_identifier("bad id", "port")


# --- check mode (P3): no connection acquired, nothing sent ---

def test_check_mode_never_acquires_a_connection():
    with patch(CONNECTION) as connect:
        result = _module([{"port": "1/1/1/1", "clear_statistics": True}], check_mode=True).execute_module()
    connect.assert_not_called()
    assert result["changed"] is True
    assert result["commands"] == [_cmd("1/1/1/1")]
    assert "response" not in result


# --- execution mechanics ---

def test_executes_one_transaction_per_command_and_returns_response():
    connection = FakeConnection(responses={_cmd("1/1/1/1"): ["ok1"], _cmd("1/1/1/2"): ["ok2"]})
    with patch(CONNECTION, return_value=connection):
        result = _module([{"port": "1/1/1/1", "clear_statistics": True},
                          {"port": "1/1/1/2", "clear_statistics": True}], check_mode=False).execute_module()
    assert connection.calls == [[_cmd("1/1/1/1")], [_cmd("1/1/1/2")]]
    assert result["response"] == ["ok1", "ok2"]


def test_partial_execution_reports_completed_failed_pending():
    connection = FakeConnection(fail_on=_cmd("1/1/1/2"))
    with patch(CONNECTION, return_value=connection):
        with pytest.raises(FakeFail) as exc:
            _module([{"port": p, "clear_statistics": True} for p in ("1/1/1/1", "1/1/1/2", "1/1/1/3")],
                    check_mode=False).execute_module()
    kw = exc.value.kwargs
    assert kw["completed"] == [_cmd("1/1/1/1")]
    assert kw["failed"] == _cmd("1/1/1/2")
    assert kw["pending"] == [_cmd("1/1/1/3")]
    assert kw["response"] == ["ok"]  # only the first command answered
    assert "unknown" in kw["msg"] and "do not blindly retry" in kw["msg"]
    assert connection.calls == [[_cmd("1/1/1/1")], [_cmd("1/1/1/2")]]  # third never sent


def test_connection_acquisition_failure_is_formatted():
    with patch(CONNECTION, side_effect=RuntimeError("no shell")):
        with pytest.raises(FakeFail) as exc:
            _module([{"port": "1/1/1/1", "clear_statistics": True}], check_mode=False).execute_module()
    assert "failed to acquire a connection" in exc.value.kwargs["msg"]
    assert "no shell" in exc.value.kwargs["msg"]


def test_rejected_command_propagates():
    connection = FakeConnection(fail_on=_cmd("1/1/1/1"), error=RuntimeError("invalid token"))
    with patch(CONNECTION, return_value=connection):
        with pytest.raises(FakeFail) as exc:
            _module([{"port": "1/1/1/1", "clear_statistics": True}], check_mode=False).execute_module()
    assert "invalid token" in exc.value.kwargs["msg"]
    assert exc.value.kwargs["completed"] == []


def test_missing_or_malformed_response_yields_empty_list():
    connection = FakeConnection(malformed=True)
    with patch(CONNECTION, return_value=connection):
        result = _module([{"port": "1/1/1/1", "clear_statistics": True}], check_mode=False).execute_module()
    assert result["response"] == []


# --- verify hook (P2): accepted != completed ---

def test_failed_verification_propagates():
    class Action(IsamActionModule):
        def build_commands(self):
            return ["admin demo clear"]

        def verify(self, commands, response):
            raise RuntimeError("operation did not complete")

    with patch(CONNECTION, return_value=FakeConnection()):
        with pytest.raises(RuntimeError, match="did not complete"):
            Action(FakeModule([], check_mode=False)).execute_module()


def test_expected_disconnect_handled_in_send_command_then_verified():
    seen = {}

    class RebootAction(IsamActionModule):
        def build_commands(self):
            return ["admin equipment slot 1/1/1 reboot"]

        def send_command(self, connection, command):
            try:
                return super(RebootAction, self).send_command(connection, command)
            except Exception:
                return []  # the reboot dropped the session: an expected disconnect

        def verify(self, commands, response):
            seen["verified"] = True

    connection = FakeConnection(fail_on="admin equipment slot 1/1/1 reboot", error=RuntimeError("session closed"))
    with patch(CONNECTION, return_value=connection):
        result = RebootAction(FakeModule([], check_mode=False)).execute_module()
    assert seen == {"verified": True}
    assert result["response"] == []


# --- base contract ---

def test_base_requires_build_commands():
    class Bare(IsamActionModule):
        pass

    with pytest.raises(NotImplementedError):
        Bare(FakeModule([])).execute_module()


def test_base_verify_hook_runs_after_execution():
    seen = {}

    class Action(IsamActionModule):
        def build_commands(self):
            return ["admin demo clear"]

        def verify(self, commands, response):
            seen["commands"] = commands
            seen["response"] = response

    with patch(CONNECTION, return_value=FakeConnection(responses={"admin demo clear": ["done"]})):
        result = Action(FakeModule([], check_mode=False)).execute_module()
    assert result["response"] == ["done"]
    assert seen == {"commands": ["admin demo clear"], "response": ["done"]}