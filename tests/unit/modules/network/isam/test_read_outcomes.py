# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Read-outcome semantics for targeted reads.

These tests pin the collection's read-result contract: a read classifies each
addressed instance independently on the command and existence axes, empty output
is never confirmed absence, and the returned string (and therefore existing
parsing) is unchanged for callers that pass no collector.
"""
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    _finalize_collector,
    _has_targeted_entries,
    _targeted_selectors,
    finish_targeted_outcomes,
    get_scoped_config,
    get_targeted_config,
    targeted_outcomes,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.read_outcomes import (
    ReadOutcomeCollector,
)


class FakeModule(object):
    def __init__(self, state="gathered", config=None):
        self.params = {"state": state}
        if config is not None:
            self.params["config"] = config
        self._fail_kwargs = None

    def fail_json(self, **kwargs):
        self._fail_kwargs = kwargs
        raise SystemExit(1)


class FakeConn(object):
    """command -> reply string, or command -> exception instance to raise."""

    def __init__(self, responses, fallback=""):
        self.responses = responses
        self.fallback = fallback
        self.commands = []

    def get(self, command):
        self.commands.append(command)
        if command in self.responses:
            value = self.responses[command]
            if isinstance(value, Exception):
                raise value
            return value
        return self.fallback


def _read(responses, selectors, require_targeted=False, state="gathered"):
    module = FakeModule(state)
    conn = FakeConn(responses)
    commands = list(responses)
    collector = ReadOutcomeCollector("bridges")
    data = get_scoped_config(
        module, conn, {}, "FALLBACK", commands,
        outcomes=collector, selectors=selectors, require_targeted=require_targeted,
    )
    return data, collector.to_result(), conn


CMD = "info configure bridge port {0} flat"


def test_present_instance_is_present():
    cmd = CMD.format("1/1/5/1/3/1/1")
    data, result, _ = _read({cmd: "configure bridge port 1/1/5/1/3/1/1 pvid 100"}, {cmd: "1/1/5/1/3/1/1"})
    assert "configure bridge port 1/1/5/1/3/1/1 pvid 100" in data
    assert result["outcomes"] == [
        {"resource": "bridges", "selector": "1/1/5/1/3/1/1", "command": "ok", "existence": "present"}
    ]


def test_confirmed_absent_via_exception():
    cmd = CMD.format("1/1/5/1/3/1/9")
    data, result, _ = _read({cmd: Exception("specified instance does not exist")}, {cmd: "1/1/5/1/3/1/9"})
    assert data == ""  # dropped from the gathered output, as before
    assert result["outcomes"][0]["command"] == "ok"
    assert result["outcomes"][0]["existence"] == "confirmed_absent"


def test_confirmed_absent_via_response_text():
    cmd = CMD.format("1/1/5/1/3/1/9")
    _, result, _ = _read({cmd: "specified instance does not exist"}, {cmd: "1/1/5/1/3/1/9"})
    assert result["outcomes"][0]["existence"] == "confirmed_absent"


def test_lower_interface_is_a_dependency_gap_not_absence():
    cmd = CMD.format("1/1/5/1/3/1/2")
    data, result, _ = _read({cmd: "lower-interface does not exist"}, {cmd: "1/1/5/1/3/1/2"})
    assert data == ""
    outcome = result["outcomes"][0]
    assert outcome["existence"] == "unknown"
    assert outcome["dependency_gap"] == "lower-interface"
    assert outcome["command"] == "ok"


def test_invalid_token_is_rejected_not_incompatible():
    cmd = CMD.format("1/1/5/1/3/1/3")
    _, result, _ = _read({cmd: "invalid token"}, {cmd: "1/1/5/1/3/1/3"})
    outcome = result["outcomes"][0]
    assert outcome["command"] == "rejected"
    assert outcome["existence"] == "unknown"
    assert "error_class" not in outcome


def test_failed_read_fails_the_module_carrying_outcomes():
    # A recorded failure must not be silently lost: the module fails carrying the
    # sanitized per-selector outcomes (fail_json -> SystemExit, which no `except
    # Exception` in a facts get_facts can swallow).
    cmd = CMD.format("1/1/5/1/3/1/4")
    conn = FakeConn({cmd: Exception("socket timeout")})
    collector = ReadOutcomeCollector("bridges")
    module = FakeModule()
    try:
        get_scoped_config(module, conn, {}, "FALLBACK", [cmd], outcomes=collector, selectors={cmd: "1/1/5/1/3/1/4"})
        assert False, "expected the failed read to fail the module"
    except SystemExit:
        pass
    fail = module._fail_kwargs
    assert fail is not None
    assert "socket timeout" in fail["msg"]
    outcome = fail["read_outcomes"]["outcomes"][0]
    assert outcome["command"] == "failed"
    assert outcome["existence"] == "unknown"
    assert outcome["error_class"] == "timeout"
    assert fail["read_outcomes"]["parse"] == "unverified"


def test_failed_read_without_collector_still_raises():
    # Legacy whole-family reads (no collector) keep the original raise behavior.
    cmd = CMD.format("1/1/5/1/3/1/4")
    conn = FakeConn({cmd: Exception("socket timeout")})
    module = FakeModule()
    try:
        get_scoped_config(module, conn, {}, "FALLBACK", [cmd])
        assert False, "expected the failed read to raise"
    except SystemExit:
        assert False, "a no-collector read must re-raise, not fail_json"
    except Exception as exc:
        assert "socket timeout" in str(exc)
    assert module._fail_kwargs is None


def test_header_only_reply_is_unknown_not_absent():
    cmd = CMD.format("1/1/5/1/3/1/5")
    data, result, _ = _read({cmd: "#---\necho info configure bridge port 1/1/5/1/3/1/5 flat"},
                            {cmd: "1/1/5/1/3/1/5"})
    assert data == ""
    outcome = result["outcomes"][0]
    assert outcome["command"] == "ok"
    assert outcome["existence"] == "unknown"


def test_mixed_read_keeps_only_present_lines():
    present = CMD.format("1/1/5/1/3/1/1")
    absent = CMD.format("1/1/5/1/3/1/9")
    data, result, _ = _read(
        {present: "configure bridge port 1/1/5/1/3/1/1 pvid 100",
         absent: "specified instance does not exist"},
        {present: "1/1/5/1/3/1/1", absent: "1/1/5/1/3/1/9"},
    )
    assert "configure bridge port 1/1/5/1/3/1/1 pvid 100" in data
    assert "1/1/5/1/3/1/9" not in data
    by_selector = {o["selector"]: o for o in result["outcomes"]}
    assert by_selector["1/1/5/1/3/1/1"]["existence"] == "present"
    assert by_selector["1/1/5/1/3/1/9"]["existence"] == "confirmed_absent"


def test_require_targeted_fails_when_no_commands():
    module = FakeModule()
    conn = FakeConn({}, fallback="FALLBACK_REPLY")
    try:
        get_scoped_config(module, conn, {}, "FALLBACK", [], require_targeted=True)
        assert False, "expected a targeted read with no commands to raise"
    except RuntimeError as exc:
        assert "refusing to widen" in str(exc)
    assert conn.commands == []  # the fallback read was never sent


def test_without_require_targeted_empty_commands_widen():
    module = FakeModule()
    conn = FakeConn({}, fallback="FALLBACK_REPLY")
    data = get_scoped_config(module, conn, {}, "FALLBACK", [])
    assert data == "FALLBACK_REPLY"
    assert conn.commands == ["FALLBACK"]


def test_no_collector_leaves_the_string_contract_unchanged():
    # Callers that pass no collector get exactly the legacy string behavior.
    present = CMD.format("1/1/5/1/3/1/1")
    absent = CMD.format("1/1/5/1/3/1/9")
    module = FakeModule()
    conn = FakeConn(
        {present: "configure bridge port 1/1/5/1/3/1/1 pvid 100",
         absent: "specified instance does not exist"})
    data = get_scoped_config(module, conn, {}, "FALLBACK", [present, absent])
    assert data == "configure bridge port 1/1/5/1/3/1/1 pvid 100"


def test_collector_result_is_sanitized_and_deterministically_ordered():
    collector = ReadOutcomeCollector("bridges")
    collector.record("b", "ok", "present")
    collector.record("a", "rejected", "unknown")
    collector.record(None, "ok", "unknown")
    collector.record_parse("unverified")
    result = collector.to_result()
    assert result["resource"] == "bridges"
    assert result["parse"] == "unverified"
    # whole-read outcome first, then selectors sorted
    assert [o["selector"] for o in result["outcomes"]] == [None, "a", "b"]
    # no raw device text anywhere in the result
    import json
    assert "does not exist" not in json.dumps(result)


# ---------------------------------------------------------------------------
# Central helpers and the get_targeted_config contract
# ---------------------------------------------------------------------------

VLAN = "info configure vlan id %s flat"
VLAN_FALLBACK = "info configure vlan id flat"


def test_targeted_outcomes_only_for_gathered():
    assert isinstance(targeted_outcomes(FakeModule("gathered", {"config": []}), "vlans"), ReadOutcomeCollector)
    assert targeted_outcomes(FakeModule("gathered"), "vlans") is not None
    assert targeted_outcomes(FakeModule("merged", {"config": []}), "vlans") is None
    assert targeted_outcomes(FakeModule("parsed"), "vlans") is None
    assert targeted_outcomes(None, "vlans") is None


def test_finalize_collector_records_default_parse():
    assert _finalize_collector(None) is None
    collector = ReadOutcomeCollector("vlans")
    collector.record("100", "ok", "present")
    result = _finalize_collector(collector)
    assert result["parse"] == "unverified"
    # an explicitly recorded parse is preserved
    collector2 = ReadOutcomeCollector("vlans")
    collector2.record_parse("complete")
    assert _finalize_collector(collector2)["parse"] == "complete"


def test_finish_targeted_outcomes_stashes_on_module():
    module = FakeModule("gathered")
    collector = ReadOutcomeCollector("vlans")
    collector.record("100", "ok", "present")
    result = finish_targeted_outcomes(module, collector)
    assert result == module._isam_read_outcomes
    assert result["outcomes"][0]["selector"] == "100"
    # no collector: no-op, nothing stashed
    module2 = FakeModule("gathered")
    assert finish_targeted_outcomes(module2, None) is None
    assert not hasattr(module2, "_isam_read_outcomes")


def test_has_targeted_entries_and_selectors():
    module = FakeModule("gathered", [{"id": "100"}, {"id": "200"}])
    formats = {"config": VLAN}
    assert _has_targeted_entries(module, "vlans", formats) is True
    assert _targeted_selectors(module, "vlans", formats) == {
        "info configure vlan id 100 flat": "100",
        "info configure vlan id 200 flat": "200",
    }
    # a named entry with an empty identity is still "explicit" but yields no selector
    module2 = FakeModule("gathered", [{"id": ""}])
    assert _has_targeted_entries(module2, "vlans", formats) is True
    assert _targeted_selectors(module2, "vlans", formats) == {}
    # no config is not explicit
    assert _has_targeted_entries(FakeModule("gathered"), "vlans", formats) is False


def test_get_targeted_config_gathered_records_outcomes():
    module = FakeModule("gathered", [{"id": "100"}, {"id": "999"}])
    present = "info configure vlan id 100 flat"
    absent = "info configure vlan id 999 flat"
    conn = FakeConn({present: "configure vlan id 100", absent: "specified instance does not exist"})
    data = get_targeted_config(module, conn, "vlans", VLAN_FALLBACK, {"config": VLAN})
    assert "configure vlan id 100" in data
    assert conn.commands == [present, absent]
    outcomes = {o["selector"]: o for o in module._isam_read_outcomes["outcomes"]}
    assert outcomes["100"]["existence"] == "present"
    assert outcomes["999"]["existence"] == "confirmed_absent"
    assert module._isam_read_outcomes["parse"] == "unverified"


def test_get_targeted_config_explicit_without_commands_refuses_to_widen():
    # config names an instance whose identity is empty: no read command can be built.
    module = FakeModule("gathered", [{"id": ""}])
    conn = FakeConn({}, fallback="FALLBACK_REPLY")
    try:
        get_targeted_config(module, conn, "vlans", VLAN_FALLBACK, {"config": VLAN})
        assert False, "expected an explicit targeted read with no commands to raise"
    except RuntimeError as exc:
        assert "refusing to widen" in str(exc)
    assert conn.commands == []  # the whole-family fallback read was never sent


def test_get_targeted_config_without_config_widens_to_whole_family():
    module = FakeModule("gathered")
    conn = FakeConn({}, fallback="WHOLE_FAMILY")
    data = get_targeted_config(module, conn, "vlans", VLAN_FALLBACK, {"config": VLAN})
    assert data == "WHOLE_FAMILY"
    assert conn.commands == [VLAN_FALLBACK]
    assert not hasattr(module, "_isam_read_outcomes")  # whole-family reads carry no outcomes


def test_get_targeted_config_write_state_reads_targeted_without_outcomes():
    module = FakeModule("merged", [{"id": "100"}])
    conn = FakeConn({"info configure vlan id 100 flat": "configure vlan id 100"})
    data = get_targeted_config(module, conn, "vlans", VLAN_FALLBACK, {"config": VLAN}, write_states=True)
    assert "configure vlan id 100" in data
    assert conn.commands == ["info configure vlan id 100 flat"]
    assert not hasattr(module, "_isam_read_outcomes")  # write states carry no outcomes


def test_get_targeted_config_failed_read_fails_carrying_all_outcomes():
    module = FakeModule("gathered", [{"id": "100"}, {"id": "200"}])
    ok_cmd = "info configure vlan id 100 flat"
    bad_cmd = "info configure vlan id 200 flat"
    conn = FakeConn({ok_cmd: "configure vlan id 100", bad_cmd: Exception("connection reset by peer")})
    try:
        get_targeted_config(module, conn, "vlans", VLAN_FALLBACK, {"config": VLAN})
        assert False, "expected the failed read to fail the module"
    except SystemExit:
        pass
    assert module._fail_kwargs is not None
    assert "connection reset by peer" in module._fail_kwargs["msg"]
    outcomes = {o["selector"]: o for o in module._fail_kwargs["read_outcomes"]["outcomes"]}
    assert outcomes["100"]["existence"] == "present"
    assert outcomes["200"]["command"] == "failed"
    assert outcomes["200"]["error_class"] == "connection_error"
