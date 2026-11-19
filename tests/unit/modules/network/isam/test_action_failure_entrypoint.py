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
