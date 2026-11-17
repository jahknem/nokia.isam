"""isam_alarm against the real 'info configure alarm flat' form (R6.2.04m lab capture).

The fixture tests/fixtures/alarm/r6.2.04m/output.txt holds the alarm part of
local_captures/DS-LIN-TEST-01/info_configure_flat.txt verbatim.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os

import pytest
from ansible.module_utils import basic

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.alarm import (
    AlarmTemplate,
)
from ansible_collections.nokia.isam.plugins.modules import isam_alarm
from ansible_collections.nokia.isam.tests.unit.modules.utils import AnsibleExitJson
from ansible_collections.nokia.isam.tests.unit.modules.network.isam.isam_module import (
    set_module_args,
)


FIXTURE = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "fixtures", "alarm", "r6.2.04m", "output.txt"
)


def _capture():
    with open(FIXTURE) as handle:
        return handle.read()


def _alarm_lines(text):
    return [line for line in text.splitlines() if line.startswith("configure alarm ")]


def _exit_json(*args, **kwargs):
    raise AnsibleExitJson(kwargs)


def _fail_json(*args, **kwargs):
    kwargs["failed"] = True
    raise AnsibleExitJson(kwargs)


class _Connection(object):
    def __init__(self, output):
        self.output = output
        self.commands = []

    def get(self, command, *args, **kwargs):
        self.commands.append(command)
        return self.output


def _run(monkeypatch, args, device_output=""):
    """Run isam_alarm with a fake connection answering every 'get' with device_output."""
    import sys

    monkeypatch.setattr(basic.AnsibleModule, "exit_json", _exit_json)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", _fail_json)
    connection = _Connection(device_output)
    for loaded in tuple(sys.modules.values()):
        if loaded is not None and hasattr(loaded, "get_resource_connection"):
            monkeypatch.setattr(loaded, "get_resource_connection", lambda *a, **k: connection)
    # Record warnings on the module itself: the global warning list is shared with (and
    # changed by) other tests.
    recorded = []
    monkeypatch.setattr(basic.AnsibleModule, "warn", lambda self, message: recorded.append(message))
    args = dict(args)
    args.setdefault("_ansible_check_mode", True)
    set_module_args(args, True)
    with pytest.raises(AnsibleExitJson) as raised:
        isam_alarm.main()
    result = raised.value.args[0]
    assert result.get("failed") is not True, result
    result["warnings"] = recorded
    return result


def _parsed(monkeypatch, text):
    return _run(monkeypatch, {"state": "parsed", "running_config": text})["parsed"]


# --- bug 1: one-line entries -------------------------------------------------

def test_capture_entry_line_is_parsed(monkeypatch):
    parsed = _parsed(monkeypatch, "configure alarm entry door severity critical service-affecting reporting logging\n")
    assert parsed["entries"] == [
        {"index": "door", "severity": "critical", "service_affecting": True, "reporting": True, "logging": True}
    ]


@pytest.mark.parametrize("line, expected", [
    ("configure alarm entry door severity major no service-affecting no reporting no logging",
     {"index": "door", "severity": "major", "service_affecting": False, "reporting": False, "logging": False}),
    ("configure alarm entry board-missing no severity service-affecting no reporting logging",
     {"index": "board-missing", "service_affecting": True, "reporting": False, "logging": True}),
    ("configure alarm entry sw-rollback severity ignore",
     {"index": "sw-rollback", "severity": "ignore"}),
    ("configure alarm entry temp-shutdown no logging",
     {"index": "temp-shutdown", "logging": False}),
    ("configure alarm entry ac-power-fail", {"index": "ac-power-fail"}),
])
def test_entry_variants(monkeypatch, line, expected):
    assert _parsed(monkeypatch, line + "\n")["entries"] == [expected]


def test_entry_attributes_on_separate_lines_are_merged(monkeypatch):
    parsed = _parsed(monkeypatch, "configure alarm entry door severity critical\nconfigure alarm entry door no reporting\n")
    assert parsed["entries"] == [{"index": "door", "severity": "critical", "reporting": False}]


def test_whole_capture_drops_nothing(monkeypatch):
    text = _capture()
    lines = _alarm_lines(text)
    parsed = _parsed(monkeypatch, text)

    entry_lines = [line for line in lines if line.startswith("configure alarm entry ")]
    filter_lines = [line for line in lines if line.startswith("configure alarm filter ")]
    profile_lines = [line for line in lines if line.startswith("configure alarm custom-profile ")]
    assert len(entry_lines) == 1 and len(filter_lines) == 62 and len(profile_lines) == 1
    assert len(parsed["entries"]) == len(entry_lines)
    assert len(parsed["filters"]) == len(filter_lines)
    assert len(parsed["custom_profiles"]) == len(profile_lines)
    assert sorted((f["fltr_type"], f["filterid"]) for f in parsed["filters"]) == sorted(
        (t, i) for t in ("spatial", "temporal") for i in range(1, 32)
    )
    assert all(f["alarmid"] == "all" for f in parsed["filters"])
    assert parsed["log"] == {"log_sev_level": "critical", "log_full_action": "wrap", "non_itf_rep_sev_level": "major"}
    assert set(parsed["delta_log"].values()) == {"wrap"} and len(parsed["delta_log"]) == 5
    assert parsed["custom_profiles"] == [{"name": "test"}]
    # every alarm line is matched by some parser
    template = AlarmTemplate()
    for line in lines:
        assert any(p["getval"].match(line) for p in template.PARSERS), line


def test_filter_line_with_all_attributes(monkeypatch):
    parsed = _parsed(monkeypatch, "configure alarm filter temporal filterid 4 alarmid door status used threshold 5 window 120\n")
    assert parsed["filters"] == [
        {"fltr_type": "temporal", "filterid": 4, "alarmid": "door", "status": "used", "threshold": 5, "window": 120}
    ]


def test_suppression_line_with_all_attributes(monkeypatch):
    text = ("configure alarm filter temporal filterid 2 alarmid all\n"
            "configure alarm suppression filterid 2 interface lt:1/1/4 alarmid board-missing status used threshold 3\n")
    parsed = _parsed(monkeypatch, text)
    assert parsed["filters"] == [{
        "fltr_type": "temporal", "filterid": 2, "alarmid": "all",
        "suppressions": [{"filterid": 2, "interface": "lt:1/1/4", "alarmid": "board-missing", "status": "used", "threshold": 3}],
    }]


# --- bug 2: entry index choices ---------------------------------------------

@pytest.mark.parametrize("index", ["door", "board-missing", "mdu-gen-mdu-env1", "ont-loopdetect"])
def test_any_device_entry_index_is_accepted(monkeypatch, index):
    result = _run(monkeypatch, {"state": "rendered", "config": {"entries": [{"index": index, "severity": "major"}]}})
    assert result["rendered"] == ["configure alarm entry %s severity major" % index]


# --- bug 3: deleted / overridden against a realistic have -------------------

def test_deleted_against_capture(monkeypatch):
    result = _run(monkeypatch, {"state": "deleted"}, _capture())
    # the 62 default filters (alarmid all only) need nothing; log/delta-log have no removal form
    assert result["commands"] == ["configure alarm entry door no severity", "configure alarm no custom-profile test"]
    assert result["changed"] is True
    assert result["warnings"] == []


def test_deleted_is_idempotent_on_default_filters(monkeypatch):
    text = "\n".join(line for line in _alarm_lines(_capture()) if " entry " not in line and "custom-profile" not in line)
    result = _run(monkeypatch, {"state": "deleted"}, text + "\n")
    assert result["commands"] == []
    assert result["changed"] is False


def test_overridden_against_capture(monkeypatch):
    config = {
        "log": {"log_sev_level": "critical", "log_full_action": "wrap", "non_itf_rep_sev_level": "major"},
        "entries": [{"index": "door", "severity": "major", "service_affecting": True, "reporting": True, "logging": True}],
        "filters": [{"fltr_type": "temporal", "filterid": 1, "alarmid": "all", "threshold": 4}],
    }
    result = _run(monkeypatch, {"state": "overridden", "config": config}, _capture())
    assert result["commands"] == [
        "configure alarm entry door severity major",
        "configure alarm filter temporal filterid 1 threshold 4",
        "configure alarm no custom-profile test",
    ]


def test_overridden_with_identical_capture_is_idempotent(monkeypatch):
    gathered = _run(monkeypatch, {"state": "gathered"}, _capture())["gathered"]
    result = _run(monkeypatch, {"state": "overridden", "config": gathered}, _capture())
    assert result["commands"] == []


def test_deleted_resets_non_default_attributes(monkeypatch):
    have = "\n".join([
        "configure alarm entry door severity critical service-affecting reporting logging",
        "configure alarm filter temporal filterid 3 alarmid door status used threshold 7 window 30",
        "configure alarm filter temporal filterid 4 alarmid all",
        "configure alarm suppression filterid 3 interface lt:1/1/4 alarmid board-init status used threshold 2",
        "configure alarm custom-profile cab mnemonic1 DOOR",
        'configure alarm hgutr069-cust cust-alm1 description "wan down"',
    ]) + "\n"
    result = _run(monkeypatch, {"state": "deleted"}, have)
    assert result["commands"] == [
        "configure alarm entry door no severity",
        "configure alarm filter temporal filterid 3 no status no threshold no window",
        "configure alarm suppression filterid 3 no status no threshold",
        "configure alarm no custom-profile cab",
        "configure alarm no hgutr069-cust cust-alm1",
    ]
    warnings = " ".join(result.get("warnings", []))
    assert "alarmid" in warnings and "interface" in warnings


def test_deleted_only_named_members(monkeypatch):
    have = "\n".join([
        "configure alarm custom-profile cab mnemonic1 DOOR",
        "configure alarm custom-profile keep mnemonic1 WATER",
        'configure alarm hgutr069-cust cust-alm1 description "wan down"',
        "configure alarm filter temporal filterid 3 alarmid all threshold 7",
    ]) + "\n"
    result = _run(monkeypatch, {"state": "deleted", "config": {"custom_profiles": [{"name": "cab"}]}}, have)
    assert result["commands"] == ["configure alarm no custom-profile cab"]


def test_merged_lists(monkeypatch):
    config = {
        "entries": [{"index": "door", "severity": "critical", "reporting": False}],
        "filters": [{"fltr_type": "spatial", "filterid": 5, "status": "used", "threshold": 3,
                     "suppressions": []},
                    {"fltr_type": "temporal", "filterid": 6, "window": 90,
                     "suppressions": [{"filterid": 6, "interface": "lt:1/1/5", "alarmid": "board-missing", "status": "used"}]}],
        "custom_profiles": [{"name": "test", "mnemonic1": "DOOR", "description1": "door open", "visible1": True}],
        "hgutr069_custs": [{"alarm_id": "cust-alm2", "description": "voip down"}],
        "delta_log": {"crit_log_full_act": "halt"},
    }
    result = _run(monkeypatch, {"state": "merged", "config": config}, _capture())
    assert result["commands"] == [
        "configure alarm entry door no reporting",
        "configure alarm filter spatial filterid 5 status used threshold 3",
        "configure alarm filter temporal filterid 6 window 90",
        "configure alarm suppression filterid 6 interface lt:1/1/5 alarmid board-missing status used",
        "configure alarm delta-log crit-log-full-act halt",
        'configure alarm custom-profile test mnemonic1 DOOR description1 "door open" visible1 enable',
        'configure alarm hgutr069-cust cust-alm2 description "voip down"',
    ]


def test_replaced_resets_omitted_attributes_of_named_members(monkeypatch):
    have = "\n".join([
        "configure alarm entry door severity critical service-affecting reporting logging",
        "configure alarm filter temporal filterid 3 alarmid all status used threshold 7",
        "configure alarm custom-profile cab mnemonic1 DOOR visible1 enable",
        "configure alarm custom-profile other mnemonic1 WATER",
    ]) + "\n"
    config = {
        "entries": [{"index": "door", "reporting": True}],
        "filters": [{"fltr_type": "temporal", "filterid": 3, "alarmid": "all", "threshold": 7}],
        "custom_profiles": [{"name": "cab", "mnemonic1": "DOOR"}],
    }
    result = _run(monkeypatch, {"state": "replaced", "config": config}, have)
    assert result["commands"] == [
        "configure alarm entry door no severity",
        "configure alarm filter temporal filterid 3 no status",
        "configure alarm custom-profile cab no visible1",
    ]


# --- bug 4: suppression without its temporal filter line --------------------

def test_suppression_without_filter_line(monkeypatch):
    text = "configure alarm suppression filterid 7 interface lt:1/1/4 alarmid board-init status used\n"
    parsed = _parsed(monkeypatch, text)
    assert parsed["filters"] == [{
        "fltr_type": "temporal", "filterid": 7,
        "suppressions": [{"filterid": 7, "interface": "lt:1/1/4", "alarmid": "board-init", "status": "used"}],
    }]


def test_suppression_attributes_on_separate_lines_are_merged(monkeypatch):
    text = ("configure alarm suppression filterid 7 interface lt:1/1/4 alarmid board-init\n"
            "configure alarm suppression filterid 7 threshold 4\n")
    parsed = _parsed(monkeypatch, text)
    assert parsed["filters"][0]["suppressions"] == [
        {"filterid": 7, "interface": "lt:1/1/4", "alarmid": "board-init", "threshold": 4}
    ]
