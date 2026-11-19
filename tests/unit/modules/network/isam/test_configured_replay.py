"""Configured offline checks for resources empty on the lab; not live write claims."""
import pytest

from .module_runner import run_module


CASES = [
    ("isam_cfm", "configure cfm domain 200 name string zztest level 3\nconfigure cfm slm inactivity-time 60\n"),
    ("isam_linetest", "configure linetest single ltsession 200 timeout-period 60\n"
                      "configure linetest single ltparm 200 resistance value1 1000\n"),
    ("isam_nat", "configure nat aging-time 240\n"),
    ("isam_error", "configure error log-full-action halt\n"),
    ("isam_cwmp_plt", "configure cwmp plt adminstate unlocked\n"),
    ("isam_pon_global", "configure pon pwrbrst-mode enable range-mode alientolerant\n"),
    ("isam_pppox_relay_global", "configure pppox-relay cross-connect global-session pado-timeout 5 pads-timeout 5\n"),
    ("isam_trouble_shooting_pon", "configure trouble-shooting pon statistics interface 1/1/6/1\n"
                                "configure trouble-shooting pon statistics threshold interval 600\n"
                                "configure trouble-shooting pon statistics threshold interface 1/1/6/1 bw-th-up 80 bw-th-dn 90\n"),
]


@pytest.mark.parametrize("module,device", CASES, ids=[case[0] for case in CASES])
@pytest.mark.parametrize("state", ["merged", "replaced"])
def test_configured_facts_reconcile_without_commands(monkeypatch, module, device, state):
    gathered = run_module(monkeypatch, module, {"state": "gathered"}, device)
    assert not gathered.get("failed"), gathered.get("msg")
    assert any(gathered["gathered"].values()), "a configured test must not pass on empty facts"
    result = run_module(monkeypatch, module, {"state": state, "config": gathered["gathered"]}, device)
    assert not result.get("failed"), result.get("msg")
    assert result["commands"] == []


@pytest.mark.parametrize("module,device", CASES, ids=[case[0] for case in CASES])
def test_configured_parse_render_parse_preserves_facts(monkeypatch, module, device):
    gathered = run_module(monkeypatch, module, {"state": "gathered"}, device)["gathered"]
    rendered = run_module(monkeypatch, module, {"state": "rendered", "config": gathered})
    assert not rendered.get("failed"), rendered.get("msg")
    assert rendered["rendered"]
    assert not any("session-cmd" in command for command in rendered["rendered"])
    reparsed = run_module(monkeypatch, module, {"state": "parsed", "running_config": "\n".join(rendered["rendered"])})
    assert reparsed["parsed"] == gathered


def test_linetest_merge_keeps_unmentioned_optional_session_settings(monkeypatch):
    device = "configure linetest single ltsession 200 timeout-period 60 group-opt extended busy-overwrite true force-measure true\n"
    result = run_module(monkeypatch, "isam_linetest", {"state": "merged", "config": {
        "sessions": [{"session_id": "200", "timeout_period": "90"}]}}, device)
    assert result["commands"] == ["configure linetest single ltsession 200 timeout-period 90"]


def test_linetest_replace_resets_only_supported_omitted_session_settings(monkeypatch):
    device = "configure linetest single ltsession 200 timeout-period 60 group-opt extended busy-overwrite true force-measure true\n"
    result = run_module(monkeypatch, "isam_linetest", {"state": "replaced", "config": {
        "sessions": [{"session_id": "200", "timeout_period": "60"}]}}, device)
    assert result["commands"] == [
        "configure linetest single ltsession 200 group-opt no",
        "configure linetest single ltsession 200 busy-overwrite no",
        "configure linetest single ltsession 200 force-measure no"]
