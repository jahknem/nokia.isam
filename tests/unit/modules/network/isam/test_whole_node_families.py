# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Fixture-driven integration tests for the whole-node targeted families.

These drive the real ``isam_interface_alarms`` / ``isam_vlan_global`` modules
and the ``isam_facts`` aggregator against a fake device answering from the
sanitized live-capture fixtures (``tests/fixtures/interface_alarms/r6.2.04m``
and ``tests/fixtures/vlan_global/r6.2.04m``, captured on a Nokia ISAM 7330
FTTN; the live probe on DS-LIN-TEST-01 confirms the same 3 alarms and the
same 10 priority-regen profiles).

Pinned whole-node contract (docs/targeted-gathering.md, "Whole-node reads"):

* one whole-node command per read, never per-instance commands;
* ``gathered`` is the unfiltered full catalog (siblings included) -- the same
  facts a whole read returns;
* per-instance outcomes: ``present`` when the parsed catalog lists the
  instance, ``unknown`` when it does not (never ``confirmed_absent`` -- the
  parser's catalog completeness is unverified), ``confirmed_absent`` only for
  the device's own node-absence signal;
* a failed read fails the module carrying the outcomes; a reply the parser
  cannot process is classified with ``parse: failed`` before the failure;
* the legacy paths are unchanged: a whole read, write states and
  ``isam_facts`` carry no ``read_outcomes``.
"""
import importlib
import sys
from pathlib import Path

import pytest
from ansible.module_utils import basic

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.interface_alarms.interface_alarms import (
    Interface_alarmsFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.vlan_global.vlan_global import (
    Isam_vlan_globalFacts,
)

from .isam_module import set_module_args
from .targeted_harness import Device, _ModuleDone, outcome_by_selector, outcomes

FIXTURES = Path(__file__).resolve().parents[4] / "fixtures"

ALARM_CMD = "info configure interface alarm"
VLAN_CMD = "info configure vlan flat"

# The sanitized live captures (r6.2.04m, 7330 FTTN): 3 configured alarms,
# 10 priority-regen profiles, plus the broadcast-frames/tpid/vmac lines.
ALARM_LINES = (FIXTURES / "interface_alarms" / "r6.2.04m" / "output.txt").read_text().splitlines()
VLAN_LINES = (FIXTURES / "vlan_global" / "r6.2.04m" / "output.txt").read_text().splitlines()

ALARM_FACTS = [
    {"name": "epon", "default_severity": "indeterminate"},
    {"name": "eont", "default_severity": "indeterminate"},
    {"name": "ont", "default_severity": "indeterminate"},
]


def _profile(pid, name, *pbits):
    entry = {"id": pid, "profile_name": name}
    for bit, value in enumerate(pbits):
        entry["pbit%d" % bit] = value
    return entry


VLAN_FACTS = {
    "broadcast_frames": {"priority_policy": "vlan-specific"},
    "priority_regen": [
        _profile(1, "TrustedPort", 0, 1, 2, 3, 4, 5, 6, 7),
        _profile(2, "BestEffort", 0, 0, 0, 0, 0, 0, 0, 0),
        _profile(3, "ControlledLoad3", 3, 3, 3, 3, 3, 3, 3, 3),
        _profile(4, "ControlledLoad4", 4, 4, 4, 4, 4, 4, 4, 4),
        _profile(5, "Background", 1, 1, 1, 1, 1, 1, 1, 1),
        _profile(6, "BE_ControlledLoad_Voice", 0, 0, 3, 3, 0, 0, 6, 6),
        _profile(7, "BE_ControlledLoad_Voice.1d", 0, 0, 0, 4, 0, 0, 6, 6),
        _profile(8, "BestEffort_Voice", 0, 0, 0, 0, 0, 0, 6, 6),
        _profile(9, "3ClassL2VPN", 0, 0, 2, 2, 4, 4, 0, 0),
        _profile(10, "4ClassL2VPN", 0, 0, 2, 2, 4, 4, 6, 6),
    ],
    "tpid": {"value": "8100"},
    "vmac_address_format": {"format": "host-id", "host_id": 0},
}


def run_module(monkeypatch, module_name, args, device):
    """Drive one real module against a fake device; the module's result dict.

    The same seam as targeted_harness.gathered, but for arbitrary args (the
    isam_facts aggregator has no state/config options).
    """
    module = importlib.import_module("ansible_collections.nokia.isam.plugins.modules." + module_name)

    def exit_json(self, **result):
        raise _ModuleDone(result)

    def fail_json(self, **result):
        raise _ModuleDone(dict(result, failed=True))

    with monkeypatch.context() as patch:
        for name, loaded in tuple(sys.modules.items()):
            if name.startswith("ansible_collections.") and hasattr(loaded, "get_resource_connection"):
                patch.setattr(loaded, "get_resource_connection", lambda *a, **kw: device)
        patch.setattr(basic.AnsibleModule, "exit_json", exit_json)
        patch.setattr(basic.AnsibleModule, "fail_json", fail_json)
        set_module_args(args, True)
        with pytest.raises(_ModuleDone) as raised:
            module.main()
        return raised.value.result


class AbsentNodeDevice(object):
    """Answers every read with the device's node-absence signal."""

    def __init__(self):
        self.commands = []

    def get(self, command, *args, **kwargs):
        self.commands.append(command)
        raise Exception("Error : instance does not exist")

    def edit_config(self, *args, **kwargs):
        raise AssertionError("gathered must not change anything")


def whole_node_device(lines):
    """A device whose only read is the whole node: it answers it with ``lines``
    exactly, unfiltered, as the real device answers the node."""
    return Device(lines, answer=lambda command, _lines: "\n".join(lines))


# ---------------------------------------------------------------------------
# isam_interface_alarms (whole node: 'info configure interface alarm')
# ---------------------------------------------------------------------------

def test_interface_alarms_whole_read_is_the_legacy_read(monkeypatch):
    device = whole_node_device(ALARM_LINES)
    result = run_module(monkeypatch, "isam_interface_alarms", {"state": "gathered"}, device)
    assert not result.get("failed"), result
    assert device.commands == [ALARM_CMD]
    assert "read_outcomes" not in result  # a whole read carries no outcomes
    assert result["gathered"] == ALARM_FACTS


def test_interface_alarms_targeted_present_reads_the_node_once(monkeypatch):
    device = whole_node_device(ALARM_LINES)
    result = run_module(monkeypatch, "isam_interface_alarms",
                        {"state": "gathered", "config": [{"name": "eont"}]}, device)
    assert not result.get("failed"), result
    assert device.commands == [ALARM_CMD]  # one whole read, nothing per-instance
    by = outcome_by_selector(result)
    assert set(by) == {"eont"}
    assert by["eont"]["section"] == "config"
    assert by["eont"]["command"] == "ok"
    assert by["eont"]["existence"] == "present"
    assert result["read_outcomes"]["parse"] == "unverified"
    # unfiltered: the siblings of the named alarm are gathered, as in a whole read
    assert result["gathered"] == ALARM_FACTS


def test_interface_alarms_targeted_absent_is_unknown_not_absent(monkeypatch):
    # The live probe's selectors: a real alarm plus one the device does not have.
    device = whole_node_device(ALARM_LINES)
    result = run_module(monkeypatch, "isam_interface_alarms",
                        {"state": "gathered", "config": [{"name": "eont"}, {"name": "no-such-alarm-zz"}]},
                        device)
    assert not result.get("failed"), result
    by = outcome_by_selector(result)
    assert by["eont"]["existence"] == "present"
    assert by["no-such-alarm-zz"]["command"] == "ok"
    assert by["no-such-alarm-zz"]["existence"] == "unknown"
    assert all(o["existence"] != "confirmed_absent" for o in outcomes(result))
    assert result["gathered"] == ALARM_FACTS  # still the full catalog


def test_interface_alarms_unrecognized_reply_line_is_unknown(monkeypatch):
    # Regression (PR review): a successful reply carrying an existing instance
    # the parser cannot recognize (a line shape no template pattern accepts).
    # The instance must surface as unknown, never confirmed_absent; the
    # recognized sibling stays present; the unrecognized line leaves no ghost
    # in gathered.
    lines = ALARM_LINES + ["configure interface alarms ont-x default-severity major"]
    device = whole_node_device(lines)
    result = run_module(monkeypatch, "isam_interface_alarms",
                        {"state": "gathered", "config": [{"name": "eont"}, {"name": "ont-x"}]}, device)
    assert not result.get("failed"), result
    by = outcome_by_selector(result)
    assert by["eont"]["existence"] == "present"
    assert by["ont-x"]["command"] == "ok"
    assert by["ont-x"]["existence"] == "unknown"
    assert result["gathered"] == ALARM_FACTS  # no ghost entry for the unrecognized line


def test_interface_alarms_empty_node_is_unknown(monkeypatch):
    device = whole_node_device([])
    result = run_module(monkeypatch, "isam_interface_alarms",
                        {"state": "gathered", "config": [{"name": "epon"}, {"name": "eont"}]}, device)
    assert not result.get("failed"), result
    assert device.commands == [ALARM_CMD]
    assert result["gathered"] == []
    assert all(o["command"] == "ok" for o in outcomes(result))
    assert all(o["existence"] == "unknown" for o in outcomes(result))


def test_interface_alarms_rejected_node_is_unknown_not_a_failure(monkeypatch):
    device = Device([], reject=True)
    result = run_module(monkeypatch, "isam_interface_alarms",
                        {"state": "gathered", "config": [{"name": "eont"}]}, device)
    assert not result.get("failed"), result
    assert device.commands == [ALARM_CMD]
    assert result["gathered"] == []
    (outcome,) = outcomes(result)
    assert outcome["command"] == "rejected"
    assert outcome["existence"] == "unknown"


def test_interface_alarms_node_absence_confirms_absence(monkeypatch):
    # The one whole-node path to confirmed_absent: the device's own signal that
    # the node does not exist -- nothing under it can be configured.
    device = AbsentNodeDevice()
    result = run_module(monkeypatch, "isam_interface_alarms",
                        {"state": "gathered", "config": [{"name": "epon"}, {"name": "eont"}]}, device)
    assert not result.get("failed"), result
    assert device.commands == [ALARM_CMD]
    assert result["gathered"] == []
    assert all(o["command"] == "ok" for o in outcomes(result))
    assert all(o["existence"] == "confirmed_absent" for o in outcomes(result))


def test_interface_alarms_failed_read_fails_carrying_outcomes(monkeypatch):
    device = Device([], fail=True)
    result = run_module(monkeypatch, "isam_interface_alarms",
                        {"state": "gathered", "config": [{"name": "eont"}]}, device)
    assert result.get("failed"), result
    (outcome,) = outcomes(result)
    assert outcome["command"] == "failed"
    assert outcome["existence"] == "unknown"
    assert outcome["error_class"] == "connection_error"


def test_interface_alarms_partial_request_sends_nothing(monkeypatch):
    # An explicit request is never served partially: an identity that is present
    # but empty fails the request before anything is sent (the gap backstop;
    # Ansible surfaces this fail as the task failure with the same message).
    device = whole_node_device(ALARM_LINES)
    module = importlib.import_module("ansible_collections.nokia.isam.plugins.modules.isam_interface_alarms")
    with monkeypatch.context() as patch:
        for name, loaded in tuple(sys.modules.items()):
            if name.startswith("ansible_collections.") and hasattr(loaded, "get_resource_connection"):
                patch.setattr(loaded, "get_resource_connection", lambda *a, **kw: device)
        patch.setattr(basic.AnsibleModule, "fail_json",
                      lambda self, **result: (_ for _ in ()).throw(_ModuleDone(dict(result, failed=True))))
        set_module_args({"state": "gathered", "config": [{"name": "eont"}, {"name": ""}]}, True)
        with pytest.raises(_ModuleDone) as raised:
            module.main()
    result = raised.value.result
    assert result["failed"] is True
    assert "config[1]" in result["msg"]
    assert "'name'" in result["msg"]
    assert "refusing" in result["msg"]
    assert device.commands == []


def test_interface_alarms_parse_failure_is_classified(monkeypatch):
    # The device replied, but the family's parser cannot process the reply:
    # parse axis 'failed', every requested instance unknown, and the module
    # fails carrying the sanitized outcomes.
    def broken_parse(self, data):
        raise ValueError("catalog shape changed")

    monkeypatch.setattr(Interface_alarmsFacts, "_parse_catalog", broken_parse)
    device = whole_node_device(ALARM_LINES)
    result = run_module(monkeypatch, "isam_interface_alarms",
                        {"state": "gathered", "config": [{"name": "eont"}]}, device)
    assert result.get("failed"), result
    assert "could not be parsed" in result["msg"]
    assert "catalog shape changed" not in result["msg"]
    assert "(ValueError)" in result["msg"]
    assert result["read_outcomes"]["parse"] == "failed"
    (outcome,) = outcomes(result)
    assert outcome["command"] == "ok"
    assert outcome["existence"] == "unknown"


def test_interface_alarms_merged_reads_whole_node_without_outcomes(monkeypatch):
    device = whole_node_device(ALARM_LINES)
    config = [{"name": name, "default_severity": "indeterminate"} for name in ("epon", "eont", "ont")]
    result = run_module(monkeypatch, "isam_interface_alarms", {"state": "merged", "config": config}, device)
    assert not result.get("failed"), result
    assert result["changed"] is False
    assert result["commands"] == []
    assert "read_outcomes" not in result
    assert device.commands == [ALARM_CMD]  # the write compares against a whole read


# ---------------------------------------------------------------------------
# isam_vlan_global (whole node: 'info configure vlan flat')
# ---------------------------------------------------------------------------

def test_vlan_global_whole_read_is_the_legacy_read(monkeypatch):
    device = whole_node_device(VLAN_LINES)
    result = run_module(monkeypatch, "isam_vlan_global", {"state": "gathered"}, device)
    assert not result.get("failed"), result
    assert device.commands == [VLAN_CMD]
    assert "read_outcomes" not in result
    assert result["gathered"] == VLAN_FACTS


def test_vlan_global_targeted_present_reads_the_node_once(monkeypatch):
    device = whole_node_device(VLAN_LINES)
    result = run_module(monkeypatch, "isam_vlan_global",
                        {"state": "gathered", "config": {"priority_regen": [{"id": 1}]}}, device)
    assert not result.get("failed"), result
    assert device.commands == [VLAN_CMD]
    by = outcome_by_selector(result)
    assert set(by) == {"1"}
    assert by["1"]["section"] == "priority_regen"
    assert by["1"]["command"] == "ok"
    assert by["1"]["existence"] == "present"
    # unfiltered: all 10 profiles are gathered, not just the named one
    assert result["gathered"] == VLAN_FACTS


def test_vlan_global_targeted_absent_is_unknown_not_absent(monkeypatch):
    # The live probe's selectors: real profile id 1 plus unconfigured id 999.
    device = whole_node_device(VLAN_LINES)
    result = run_module(monkeypatch, "isam_vlan_global",
                        {"state": "gathered", "config": {"priority_regen": [{"id": 1}, {"id": 999}]}},
                        device)
    assert not result.get("failed"), result
    by = outcome_by_selector(result)
    assert by["1"]["existence"] == "present"
    assert by["999"]["command"] == "ok"
    assert by["999"]["existence"] == "unknown"
    assert all(o["existence"] != "confirmed_absent" for o in outcomes(result))
    assert [entry["id"] for entry in result["gathered"]["priority_regen"]] == list(range(1, 11))


def test_vlan_global_unrecognized_profile_line_is_unknown(monkeypatch):
    # Regression (PR review): the reviewer's exact scenario -- a successful
    # reply carrying an existing profile whose line the strict ordered template
    # regex cannot recognize (an unfamiliar attribute). The profile must
    # surface as unknown, never confirmed_absent; the recognized sibling stays
    # present; no ghost profile in gathered.
    lines = VLAN_LINES + [
        "configure vlan priority-regen 11 profile-name NewAttribute pbit0 0 extra-attribute 9 pbit1 1",
    ]
    device = whole_node_device(lines)
    result = run_module(monkeypatch, "isam_vlan_global",
                        {"state": "gathered", "config": {"priority_regen": [{"id": 1}, {"id": 11}]}},
                        device)
    assert not result.get("failed"), result
    by = outcome_by_selector(result)
    assert by["1"]["existence"] == "present"
    assert by["11"]["command"] == "ok"
    assert by["11"]["existence"] == "unknown"
    assert result["gathered"] == VLAN_FACTS  # no ghost profile 11


def test_vlan_global_empty_node_is_unknown(monkeypatch):
    device = whole_node_device([])
    result = run_module(monkeypatch, "isam_vlan_global",
                        {"state": "gathered", "config": {"priority_regen": [{"id": 1}, {"id": 2}]}}, device)
    assert not result.get("failed"), result
    assert device.commands == [VLAN_CMD]
    assert result["gathered"] == {}
    assert all(o["command"] == "ok" for o in outcomes(result))
    assert all(o["existence"] == "unknown" for o in outcomes(result))


def test_vlan_global_rejected_node_is_unknown_not_a_failure(monkeypatch):
    device = Device([], reject=True)
    result = run_module(monkeypatch, "isam_vlan_global",
                        {"state": "gathered", "config": {"priority_regen": [{"id": 1}]}}, device)
    assert not result.get("failed"), result
    assert device.commands == [VLAN_CMD]
    assert result["gathered"] == {}
    (outcome,) = outcomes(result)
    assert outcome["command"] == "rejected"
    assert outcome["existence"] == "unknown"


def test_vlan_global_node_absence_confirms_absence(monkeypatch):
    device = AbsentNodeDevice()
    result = run_module(monkeypatch, "isam_vlan_global",
                        {"state": "gathered", "config": {"priority_regen": [{"id": 1}, {"id": 2}]}}, device)
    assert not result.get("failed"), result
    assert device.commands == [VLAN_CMD]
    assert result["gathered"] == {}
    assert all(o["command"] == "ok" for o in outcomes(result))
    assert all(o["existence"] == "confirmed_absent" for o in outcomes(result))


def test_vlan_global_failed_read_fails_carrying_outcomes(monkeypatch):
    device = Device([], fail=True)
    result = run_module(monkeypatch, "isam_vlan_global",
                        {"state": "gathered", "config": {"priority_regen": [{"id": 1}]}}, device)
    assert result.get("failed"), result
    (outcome,) = outcomes(result)
    assert outcome["command"] == "failed"
    assert outcome["existence"] == "unknown"
    assert outcome["error_class"] == "connection_error"


def test_vlan_global_partial_request_sends_nothing(monkeypatch):
    # A profile entry without its identity field: the argspec (id is required)
    # rejects the request before anything is sent.
    device = whole_node_device(VLAN_LINES)
    module = importlib.import_module("ansible_collections.nokia.isam.plugins.modules.isam_vlan_global")
    with monkeypatch.context() as patch:
        for name, loaded in tuple(sys.modules.items()):
            if name.startswith("ansible_collections.") and hasattr(loaded, "get_resource_connection"):
                patch.setattr(loaded, "get_resource_connection", lambda *a, **kw: device)
        patch.setattr(basic.AnsibleModule, "fail_json",
                      lambda self, **result: (_ for _ in ()).throw(_ModuleDone(dict(result, failed=True))))
        set_module_args({"state": "gathered", "config": {"priority_regen": [{"id": 1}, {}]}}, True)
        with pytest.raises(_ModuleDone) as raised:
            module.main()
    result = raised.value.result
    assert result["failed"] is True
    assert "missing required arguments" in result["msg"]
    assert "priority_regen" in result["msg"]
    assert device.commands == []


def test_vlan_global_parse_failure_is_classified(monkeypatch):
    def broken_parse(self, data):
        raise ValueError("catalog shape changed")

    monkeypatch.setattr(Isam_vlan_globalFacts, "_parse_config", broken_parse)
    device = whole_node_device(VLAN_LINES)
    result = run_module(monkeypatch, "isam_vlan_global",
                        {"state": "gathered", "config": {"priority_regen": [{"id": 1}]}}, device)
    assert result.get("failed"), result
    assert "could not be parsed" in result["msg"]
    assert "catalog shape changed" not in result["msg"]
    assert "(ValueError)" in result["msg"]
    assert result["read_outcomes"]["parse"] == "failed"
    (outcome,) = outcomes(result)
    assert outcome["command"] == "ok"
    assert outcome["existence"] == "unknown"


def test_vlan_global_merged_reads_whole_node_without_outcomes(monkeypatch):
    device = whole_node_device(VLAN_LINES)
    config = {"priority_regen": [_profile(1, "TrustedPort", 0, 1, 2, 3, 4, 5, 6, 7)]}
    result = run_module(monkeypatch, "isam_vlan_global", {"state": "merged", "config": config}, device)
    assert not result.get("failed"), result
    assert result["changed"] is False
    assert result["commands"] == []
    assert "read_outcomes" not in result
    assert device.commands == [VLAN_CMD]


# ---------------------------------------------------------------------------
# isam_facts: the aggregator's whole-read path (the NOC's main read path)
# ---------------------------------------------------------------------------

def test_isam_facts_interface_alarms_whole_read_path(monkeypatch):
    device = whole_node_device(ALARM_LINES)
    result = run_module(monkeypatch, "isam_facts", {"gather_network_resources": ["interface_alarms"]}, device)
    assert not result.get("failed"), result
    assert device.commands == [ALARM_CMD]
    resources = result["ansible_facts"]["ansible_network_resources"]
    assert resources["interface_alarms"] == ALARM_FACTS
    assert "read_outcomes" not in result


def test_isam_facts_vlan_global_whole_read_path(monkeypatch):
    device = whole_node_device(VLAN_LINES)
    result = run_module(monkeypatch, "isam_facts", {"gather_network_resources": ["isam_vlan_global"]}, device)
    assert not result.get("failed"), result
    assert device.commands == [VLAN_CMD]
    resources = result["ansible_facts"]["ansible_network_resources"]
    assert resources["isam_vlan_global"] == VLAN_FACTS
    assert "read_outcomes" not in result


def test_isam_facts_both_whole_node_families_in_one_run(monkeypatch):
    # A device answering the whole node for both families at once: each family
    # parses its own lines and ignores the other's (the real parsers' noise
    # tolerance on live output).
    device = whole_node_device(ALARM_LINES + VLAN_LINES)
    result = run_module(monkeypatch, "isam_facts",
                        {"gather_network_resources": ["interface_alarms", "isam_vlan_global"]}, device)
    assert not result.get("failed"), result
    assert sorted(device.commands) == sorted([ALARM_CMD, VLAN_CMD])
    resources = result["ansible_facts"]["ansible_network_resources"]
    assert resources["interface_alarms"] == ALARM_FACTS
    assert resources["isam_vlan_global"] == VLAN_FACTS
