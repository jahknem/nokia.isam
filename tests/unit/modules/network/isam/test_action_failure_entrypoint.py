"""Real Ansible JSON failure serialization, not a fail_json stand-in."""
import json

import pytest

from ansible_collections.nokia.isam.plugins.modules import isam_security_ext_authenticator
from ansible_collections.nokia.isam.plugins.module_utils.network.isam import action_module
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.security_ext_authenticator.security_ext_authenticator import (
    Isam_security_ext_authenticator,
)

from .isam_module import set_module_args


COMMANDS = ["admin security ext-authenticator 1/1/6/%s clear-statistics" % port for port in (1, 2, 3)]


class Connection:
    def __init__(self, fail_on=None):
        self.fail_on = fail_on
        self.calls = []

    def edit_config(self, candidate):
        self.calls.append(candidate)
        if candidate == [self.fail_on]:
            raise RuntimeError("device refused command")
        return {"response": ["accepted"]}


def invoke(capsys):
    # Keep AnsibleModule.fail_json and exit_json untouched: these call SystemExit
    # after serializing failed=True, invocation data and the supplied failure fields.
    set_module_args({"config": [{"port": "1/1/6/%s" % port, "clear_statistics": True}
                                for port in (1, 2, 3)], "_ansible_check_mode": False}, True)
    with pytest.raises(SystemExit) as exited:
        isam_security_ext_authenticator.main()
    assert exited.value.code == 1
    return json.loads(capsys.readouterr().out)


def test_partial_failure_retains_command_identity_through_real_fail_json(monkeypatch, capsys):
    connection = Connection(fail_on=COMMANDS[1])
    monkeypatch.setattr(action_module, "get_resource_connection", lambda module: connection)
    result = invoke(capsys)
    assert result["failed"] is True
    assert result["failed_command"] == COMMANDS[1]
    assert result["commands"] == COMMANDS
    assert result["completed"] == [COMMANDS[0]]
    assert result["pending"] == [COMMANDS[2]]
    assert result["response"] == ["accepted"]
    assert connection.calls == [[COMMANDS[0]], [COMMANDS[1]]]


def test_verification_exception_retains_execution_context_without_retry(monkeypatch, capsys):
    connection = Connection()
    monkeypatch.setattr(action_module, "get_resource_connection", lambda module: connection)

    def fail_verification(self, commands, response):
        raise RuntimeError("follow-up read unavailable")

    monkeypatch.setattr(Isam_security_ext_authenticator, "verify", fail_verification)
    result = invoke(capsys)
    assert result["failed"] is True and result["changed"] is True
    assert result["failure_phase"] == "verification"
    assert result["completion_status"] == "unknown"
    assert result["commands"] == result["accepted"] == COMMANDS
    assert result["completed"] == result["pending"] == []
    assert result["failed_command"] is None
    assert result["response"] == ["accepted"] * 3
    assert "do not blindly retry" in result["msg"]
    assert connection.calls == [[command] for command in COMMANDS]


SCHEMA = {"commands", "sent", "accepted", "completed", "failed_command", "pending", "failure_phase",
          "completion_status", "response", "changed"}


def test_execution_failure_uses_the_shared_schema(monkeypatch, capsys):
    connection = Connection(fail_on=COMMANDS[1])
    monkeypatch.setattr(action_module, "get_resource_connection", lambda module: connection)
    result = invoke(capsys)
    assert SCHEMA <= set(result)
    assert result["failure_phase"] == "execution"
    assert result["completion_status"] == "unknown"
    assert result["sent"] == COMMANDS[:2]
    assert result["accepted"] == [COMMANDS[0]]
    # the default verify trusts the transport: accepted counts as completed
    assert result["completed"] == [COMMANDS[0]]


def test_execution_failure_with_own_verify_does_not_claim_completion(monkeypatch, capsys):
    # verify never ran for the accepted commands, so their completion is unknown
    connection = Connection(fail_on=COMMANDS[1])
    monkeypatch.setattr(action_module, "get_resource_connection", lambda module: connection)
    monkeypatch.setattr(Isam_security_ext_authenticator, "verify", lambda self, commands, response: None)
    result = invoke(capsys)
    assert result["accepted"] == [COMMANDS[0]]
    assert result["completed"] == []


def test_verification_failure_uses_the_shared_schema(monkeypatch, capsys):
    connection = Connection()
    monkeypatch.setattr(action_module, "get_resource_connection", lambda module: connection)

    def fail_verification(self, commands, response):
        raise RuntimeError("follow-up read unavailable")

    monkeypatch.setattr(Isam_security_ext_authenticator, "verify", fail_verification)
    result = invoke(capsys)
    assert SCHEMA <= set(result)
    assert result["sent"] == result["accepted"] == COMMANDS


def test_connection_failure_uses_the_shared_schema(monkeypatch, capsys):
    def no_connection(module):
        raise RuntimeError("socket missing")

    monkeypatch.setattr(action_module, "get_resource_connection", no_connection)
    result = invoke(capsys)
    assert SCHEMA <= set(result)
    assert result["failure_phase"] == "connection"
    assert result["completion_status"] == "not_started"
    assert result["sent"] == result["accepted"] == result["completed"] == []
    assert result["pending"] == COMMANDS and result["changed"] is False


def test_success_reports_the_same_outcome_fields(monkeypatch, capsys):
    connection = Connection()
    monkeypatch.setattr(action_module, "get_resource_connection", lambda module: connection)
    set_module_args({"config": [{"port": "1/1/6/1", "clear_statistics": True}], "_ansible_check_mode": False}, True)
    with pytest.raises(SystemExit) as exited:
        isam_security_ext_authenticator.main()
    result = json.loads(capsys.readouterr().out)
    assert exited.value.code == 0
    assert result["sent"] == result["accepted"] == result["completed"] == [COMMANDS[0]]
