from textwrap import dedent

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.linetest import LinetestTemplate



def test_linetest_parse_ignores_test_actions():
    parsed = LinetestTemplate().parse(dedent("""
        configure linetest single ltsession 3 session-cmd create timeout-period 120 test-mode single
        configure linetest single ltparm 3 resist-tr(ohm) value1 1 min-threshold 10
    """))
    assert parsed["sessions"] == [{"session_id": "3", "timeout_period": "120", "test_mode": "single"}]
    assert parsed["parameters"] == [{
        "session_id": "3", "test_name": "resist-tr(ohm)", "value1": "1", "min_threshold": "10",
    }]


def test_linetest_render_is_configuration_only():
    commands = LinetestTemplate().render({"sessions": [{"session_id": "1", "timeout_period": "120"}], "parameters": []})
    assert commands == ["configure linetest single ltsession 1 timeout-period 120"]
    assert all("session-cmd" not in command for command in commands)


def test_linetest_parse_supports_unset_optional_fields():
    parsed = LinetestTemplate().parse(
        "configure linetest single ltsession 1 no group-opt no busy-overwrite"
    )
    assert parsed["sessions"] == [{
        "session_id": "1", "group_opt": None, "busy_overwrite": None,
    }]


# --- state behaviour pinned for the IsamResourceModule migration ---

from .module_runner import run_module

LT_DEVICE = (
    "configure linetest single ltsession 1 timeout-period 60 test-mode single\n"
    "configure linetest single ltsession 2 timeout-period 90\n"
    "configure linetest single ltparm 1 resist-tr(ohm) value1 1 min-threshold 10\n"
)


def _lt(monkeypatch, state, config=None, running=LT_DEVICE):
    if state == "parsed":
        return run_module(monkeypatch, "isam_linetest", {"state": "parsed", "running_config": running})
    args = {"state": state} if config is None else {"state": state, "config": config}
    return run_module(monkeypatch, "isam_linetest", args, running)


def test_lt_merged_changes_only_given_field(monkeypatch):
    assert _lt(monkeypatch, "merged", {"sessions": [{"session_id": "1", "timeout_period": "120"}]})["commands"] == [
        "configure linetest single ltsession 1 timeout-period 120"]


def test_lt_merged_idempotent(monkeypatch):
    gathered = _lt(monkeypatch, "gathered")["gathered"]
    assert _lt(monkeypatch, "merged", gathered)["commands"] == []


def test_lt_deleted_session_uses_destroy(monkeypatch):
    assert _lt(monkeypatch, "deleted", {"sessions": [{"session_id": "1"}]})["commands"] == [
        "configure linetest single ltsession 1 session-cmd destroy"]


def test_lt_deleted_preserves_siblings(monkeypatch):
    cmds = _lt(monkeypatch, "deleted", {"sessions": [{"session_id": "1"}]})["commands"]
    assert cmds == ["configure linetest single ltsession 1 session-cmd destroy"]
    assert all("ltsession 2" not in c for c in cmds)


def test_lt_deleted_without_config_destroys_all_sessions(monkeypatch):
    cmds = _lt(monkeypatch, "deleted")["commands"]
    assert "configure linetest single ltsession 1 session-cmd destroy" in cmds
    assert "configure linetest single ltsession 2 session-cmd destroy" in cmds


def test_lt_deleted_parameters_only_fails(monkeypatch):
    res = _lt(monkeypatch, "deleted", {"parameters": [{"session_id": "1", "test_name": "resist-tr(ohm)"}]})
    assert res.get("failed") and "no supported delete command" in res["msg"]


def test_lt_overridden_destroys_unrequested_sessions(monkeypatch):
    cmds = _lt(monkeypatch, "overridden", {"sessions": [{"session_id": "1", "timeout_period": "60"}],
                                           "parameters": [{"session_id": "1", "test_name": "resist-tr(ohm)", "value1": "1", "min_threshold": "10"}]})["commands"]
    assert "configure linetest single ltsession 2 session-cmd destroy" in cmds
    assert all("ltsession 1 session-cmd destroy" not in c for c in cmds)


def test_lt_overridden_unrequested_parameters_fail(monkeypatch):
    res = _lt(monkeypatch, "overridden", {"sessions": [{"session_id": "1", "timeout_period": "60"}, {"session_id": "2", "timeout_period": "90"}]})
    assert res.get("failed") and "no supported delete command" in res["msg"]


def test_lt_overridden_session_removal_also_removes_its_parameters(monkeypatch):
    # Parameters under omitted session 1 disappear with it. Session 2 remains;
    # no standalone parameter deletion (or test action) should be attempted.
    result = _lt(monkeypatch, "overridden", {"sessions": [{"session_id": "2", "timeout_period": "90"}]})
    assert not result.get("failed"), result.get("msg")
    assert result["commands"] == ["configure linetest single ltsession 1 session-cmd destroy"]


def test_lt_rendered_is_configuration_only(monkeypatch):
    # Ansible-injected None options are omissions, not reset requests.
    rendered = _lt(monkeypatch, "rendered", {"sessions": [{"session_id": "1", "timeout_period": "120"}]})["rendered"]
    assert "configure linetest single ltsession 1 timeout-period 120" in rendered
    assert rendered == ["configure linetest single ltsession 1 timeout-period 120"]
    assert all("session-cmd" not in c for c in rendered)


def test_lt_parsed_ignores_actions(monkeypatch):
    parsed = _lt(monkeypatch, "parsed", running="configure linetest single ltsession 3 session-cmd create timeout-period 120\n")["parsed"]
    assert parsed["sessions"] == [{"session_id": "3", "timeout_period": "120"}]
