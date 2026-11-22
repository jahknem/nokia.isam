# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""End-to-end read-outcome contract for targeted gathering, on representative families.

Drives the real module (``state: gathered`` with ``config`` naming instances) against
a fake device and pins the five read behaviors on three identity shapes:

* ``vlans``        -- simple identity (one scalar field, config is the list)
* ``qos_profiles`` -- composite identity (two fields, joined by '/' in the selector)
* ``system``       -- nested config (dotted section ``sntp.servers``)

Behaviors: present, confirmed absent, unknown (header-only reply), failed (command
error: the module fails carrying ``read_outcomes``), rejected (the device rejects the
selector, "invalid token"). Backward compatibility: whole-family reads carry no
outcomes, the gathered string contract is unchanged, and an explicit request that
yields no read command fails rather than silently widening to the whole family.
"""
import json

import pytest

from . import targeted_harness as harness
from .targeted_cases_a import CASES as _CASES_A
from .targeted_cases_c import CASES as _CASES_C

CASES = {}
CASES.update(_CASES_A)
CASES.update(_CASES_C)

# (case name, target selector, sibling selector, targeted read command sent)
REPRESENTATIVE = [
    ("vlans", "100", "1000", "info configure vlan id 100 flat"),
    ("qos_profiles", "scheduler-node/SN_Alpha", "marker-d1p/MK_Beta",
     "info configure qos profiles scheduler-node SN_Alpha flat"),
    ("system:sntp.servers", "198.51.100.7", "203.0.113.9",
     "info configure system sntp server-table ip-address 198.51.100.7 flat"),
]


@pytest.mark.parametrize("name,selector,sibling,command", REPRESENTATIVE)
def test_present(monkeypatch, name, selector, sibling, command):
    case = CASES[name]
    full = harness.full_commands(monkeypatch, case)
    device = harness.Device(case["lines"] + case["sibling"], full=full)
    result = harness.gathered(monkeypatch, case, case["config"], device)
    assert not result.get("failed"), result
    # exactly the targeted command was sent; the whole-family read never was
    assert device.commands == [command]
    outcomes = harness.outcome_by_selector(result)
    assert set(outcomes) == {selector}
    assert outcomes[selector]["command"] == "ok"
    assert outcomes[selector]["existence"] == "present"
    assert outcomes[selector]["resource"] == harness.resource_of(name)
    # no parser records coverage for these families: the default parse outcome
    assert result["read_outcomes"]["parse"] == "unverified"
    # the gathered string contract is unchanged
    assert case["marker"] in harness.text(result)
    assert case["sibling_marker"] not in harness.text(result)


@pytest.mark.parametrize("name,selector,sibling,command", REPRESENTATIVE)
def test_confirmed_absent(monkeypatch, name, selector, sibling, command):
    case = CASES[name]
    full = harness.full_commands(monkeypatch, case)
    device = harness.Device([], full=full)
    result = harness.gathered(monkeypatch, case, case["config"], device)
    assert not result.get("failed"), result
    assert device.commands == [command]
    outcomes = harness.outcome_by_selector(result)
    assert set(outcomes) == {selector}
    assert outcomes[selector]["command"] == "ok"
    assert outcomes[selector]["existence"] == "confirmed_absent"
    assert case["marker"] not in harness.text(result)


@pytest.mark.parametrize("name,selector,sibling,command", REPRESENTATIVE)
def test_header_only_reply_is_unknown(monkeypatch, name, selector, sibling, command):
    # The device answers the addressed instance with only the header, exactly like a
    # non-existing one: the reply is dropped, and the existence is unknown -- never
    # presence, never confirmed absence.
    case = CASES[name]
    full = harness.full_commands(monkeypatch, case)
    device = harness.Device([], full=full, header=True)
    result = harness.gathered(monkeypatch, case, case["config"], device)
    assert not result.get("failed"), result
    assert device.commands == [command]
    outcomes = harness.outcome_by_selector(result)
    assert set(outcomes) == {selector}
    assert outcomes[selector]["command"] == "ok"
    assert outcomes[selector]["existence"] == "unknown"
    assert case["marker"] not in harness.text(result)


@pytest.mark.parametrize("name,selector,sibling,command", REPRESENTATIVE)
def test_command_failure_fails_carrying_outcomes(monkeypatch, name, selector, sibling, command):
    # A recorded failure must not be silently lost: the module fails carrying the
    # sanitized per-selector read_outcomes.
    case = CASES[name]
    device = harness.Device([], fail=True)
    result = harness.gathered(monkeypatch, case, case["config"], device)
    assert result.get("failed"), result
    assert "connection to the device was lost" in result["msg"]
    outcomes = harness.outcome_by_selector(result)
    assert set(outcomes) == {selector}
    assert outcomes[selector]["command"] == "failed"
    assert outcomes[selector]["existence"] == "unknown"
    assert outcomes[selector]["error_class"] == "connection_error"
    assert result["read_outcomes"]["parse"] == "unverified"
    # sanitized: no raw device text in the outcomes
    assert "device was lost" not in json.dumps(result["read_outcomes"])


@pytest.mark.parametrize("name,selector,sibling,command", REPRESENTATIVE)
def test_rejected_selector_is_unknown(monkeypatch, name, selector, sibling, command):
    # The device rejects the addressed selector ("invalid token"): for a read that is
    # 'nothing configured here' (existence unknown), not a failure.
    case = CASES[name]
    full = harness.full_commands(monkeypatch, case)
    device = harness.Device([], full=full, reject=True)
    result = harness.gathered(monkeypatch, case, case["config"], device)
    assert not result.get("failed"), result
    assert device.commands == [command]
    outcomes = harness.outcome_by_selector(result)
    assert set(outcomes) == {selector}
    assert outcomes[selector]["command"] == "rejected"
    assert outcomes[selector]["existence"] == "unknown"
    assert case["marker"] not in harness.text(result)


@pytest.mark.parametrize("name,selector,sibling,command", REPRESENTATIVE)
def test_several_instances_are_each_labeled(monkeypatch, name, selector, sibling, command):
    case = CASES[name]
    full = harness.full_commands(monkeypatch, case)
    device = harness.Device(case["lines"] + case["sibling"], full=full)
    config = harness.merge(case["config"], case["sibling_config"])
    result = harness.gathered(monkeypatch, case, config, device)
    assert not result.get("failed"), result
    assert not set(device.commands) & full, device.commands
    assert case["marker"] in harness.text(result) and case["sibling_marker"] in harness.text(result)
    outcomes = harness.outcome_by_selector(result)
    assert set(outcomes) == {selector, sibling}
    assert all(o["command"] == "ok" and o["existence"] == "present" for o in outcomes.values())


@pytest.mark.parametrize("name,selector,sibling,command", REPRESENTATIVE)
def test_whole_family_read_carries_no_outcomes(monkeypatch, name, selector, sibling, command):
    # Backward compatibility: without config the whole resource is read, as before,
    # and the result carries no read_outcomes at all.
    case = CASES[name]
    full = harness.full_commands(monkeypatch, case)
    device = harness.Device(case["lines"] + case["sibling"], full=full)
    result = harness.gathered(monkeypatch, case, None, device)
    assert not result.get("failed"), result
    assert set(device.commands) <= full, device.commands
    assert case["marker"] in harness.text(result) and case["sibling_marker"] in harness.text(result)
    assert "read_outcomes" not in result


def test_explicit_request_without_commands_fails(monkeypatch):
    # An invalid selector: the named instance's identity cannot become a read command.
    # The read fails with a clear message; the whole-family read is never sent.
    case = CASES["vlans"]
    device = harness.Device([], full=harness._AllFull())
    result = harness.gathered(monkeypatch, case, [{"id": ""}], device)
    assert result.get("failed"), result
    assert "refusing to widen" in result["msg"]
    assert device.commands == []
    assert "read_outcomes" not in result
