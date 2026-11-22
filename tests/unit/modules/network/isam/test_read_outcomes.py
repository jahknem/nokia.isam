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
    get_scoped_config,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.read_outcomes import (
    ReadOutcomeCollector,
)


class FakeModule(object):
    def __init__(self, state="gathered"):
        self.params = {"state": state}


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


def test_failed_read_raises_and_records_failed():
    cmd = CMD.format("1/1/5/1/3/1/4")
    conn = FakeConn({cmd: Exception("socket timeout")})
    collector = ReadOutcomeCollector("bridges")
    module = FakeModule()
    try:
        get_scoped_config(module, conn, {}, "FALLBACK", [cmd], outcomes=collector, selectors={cmd: "1/1/5/1/3/1/4"})
        assert False, "expected the failed read to raise"
    except Exception as exc:
        assert "socket timeout" in str(exc)
    outcome = collector.to_result()["outcomes"][0]
    assert outcome["command"] == "failed"
    assert outcome["existence"] == "unknown"
    assert outcome["error_class"] == "timeout"


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
