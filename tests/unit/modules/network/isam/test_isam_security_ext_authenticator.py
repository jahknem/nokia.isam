from ansible_collections.nokia.isam.plugins.module_utils.network.isam.action_module import IsamActionModule
from ansible_collections.nokia.isam.plugins.modules import isam_security_ext_authenticator
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args
from .module_runner import run_module

CONNECTION = "ansible_collections.nokia.isam.plugins.module_utils.network.isam.action_module.get_resource_connection"


def _run(monkeypatch, config):
    return run_module(monkeypatch, "isam_security_ext_authenticator", {"config": config})


# --- the operation is required: a bare resource path only navigates, it is not an action ---

def test_clear_statistics_is_required(monkeypatch):
    res = _run(monkeypatch, [{"port": "1/1/1/1"}])
    assert res.get("failed") and "explicit operation" in res["msg"]
    res = _run(monkeypatch, [{"port": "1/1/1/1", "clear_statistics": False}])
    assert res.get("failed") and "explicit operation" in res["msg"]


def test_one_entry_without_operation_fails_the_whole(monkeypatch):
    res = _run(monkeypatch, [{"port": "1/1/1/1", "clear_statistics": True}, {"port": "1/1/1/2"}])
    assert res.get("failed") and "explicit operation" in res["msg"]


def test_check_mode_reports_commands_without_connecting(monkeypatch):
    res = _run(monkeypatch, [{"port": "1/1/1/1", "clear_statistics": True},
                             {"port": "1/1/1/2", "clear_statistics": True}])
    assert res["changed"] is True
    assert res["commands"] == [
        "admin security ext-authenticator 1/1/1/1 clear-statistics",
        "admin security ext-authenticator 1/1/1/2 clear-statistics",
    ]
    assert res["_sent"] == []  # nothing sent in check mode
    assert "response" not in res


# --- execution mechanics (the IsamActionModule base) ---

class FakeConnection:
    def __init__(self, response=None, error=None):
        self.sent = []
        self._response = response or []
        self._error = error

    def edit_config(self, candidate):
        self.sent.extend(candidate)
        if self._error:
            raise self._error
        return {"request": list(candidate), "response": self._response}


class TestActionExecution(TestIsamModule):
    module = isam_security_ext_authenticator

    def test_executes_and_returns_response(self):
        connection = FakeConnection(response=["ok"])
        with patch(CONNECTION, return_value=connection):
            set_module_args({"config": [{"port": "1/1/1/1", "clear_statistics": True}]}, False)
            result = self.execute_module(changed=True)
        self.assertEqual(connection.sent, ["admin security ext-authenticator 1/1/1/1 clear-statistics"])
        self.assertEqual(result["commands"], ["admin security ext-authenticator 1/1/1/1 clear-statistics"])
        self.assertEqual(result["response"], ["ok"])

    def test_execution_failure_propagates(self):
        connection = FakeConnection(error=RuntimeError("device refused"))
        with patch(CONNECTION, return_value=connection):
            set_module_args({"config": [{"port": "1/1/1/1", "clear_statistics": True}]}, False)
            result = self.execute_module(failed=True)
        self.assertIn("device refused", result["msg"])
        self.assertEqual(result["commands"], ["admin security ext-authenticator 1/1/1/1 clear-statistics"])


def test_base_requires_build_commands():
    class Bare(IsamActionModule):
        pass

    module = type("M", (), {"check_mode": True, "params": {}})()
    try:
        Bare(module).execute_module()
        assert False, "expected NotImplementedError"
    except NotImplementedError:
        pass


def test_base_verify_hook_runs_after_execution():
    seen = {}

    class Action(IsamActionModule):
        def build_commands(self):
            return ["admin demo clear"]

        def verify(self, commands, response):
            seen["commands"] = commands
            seen["response"] = response

    module = type("M", (), {"check_mode": False, "params": {}})()
    with patch(CONNECTION, return_value=FakeConnection(response=["done"])):
        result = Action(module).execute_module()
    assert result["response"] == ["done"]
    assert seen == {"commands": ["admin demo clear"], "response": ["done"]}
