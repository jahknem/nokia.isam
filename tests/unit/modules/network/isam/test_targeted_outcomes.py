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
cannot be read in full fails rather than silently widening to the whole family or
serving a subset. The final section pins the review-finding regressions: the
conservative multi-read merge, per-section attribution of shared identity values,
partial requests, and failed bare-instance detail probes.
"""
import json

import pytest

from . import targeted_harness as harness
from .targeted_cases_a import CASES as _CASES_A
from .targeted_cases_c import CASES as _CASES_C
from .targeted_cases_core import CASES as _CASES_CORE

CASES = {}
CASES.update(_CASES_A)
CASES.update(_CASES_C)
CASES.update(_CASES_CORE)

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
    # Sanitized like the outcomes: the error class and selector, no raw transport text.
    assert "connection to the device was lost" not in result["msg"]
    assert "(connection_error)" in result["msg"] and selector in result["msg"], result["msg"]
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
    assert "config[0]" in result["msg"] and "refusing" in result["msg"], result["msg"]
    assert device.commands == []
    assert "read_outcomes" not in result


# ---------------------------------------------------------------------------
# Review findings: conservative merge, section attribution, partial requests,
# and failed bare-instance probes
# ---------------------------------------------------------------------------


def test_partial_identity_request_fails_without_commands(monkeypatch):
    # One of several named instances has no identity: an explicit request is never
    # served partially -- the module fails before sending anything (regression: the
    # valid instance used to be read while the invalid one was silently dropped).
    case = CASES["vlans"]
    device = harness.Device([], full=harness._AllFull())
    result = harness.gathered(monkeypatch, case, [{"id": "100"}, {"id": ""}], device)
    assert result.get("failed"), result
    assert "config[1]" in result["msg"] and "refusing" in result["msg"], result["msg"]
    assert device.commands == []  # not even the valid instance's read was sent
    assert "read_outcomes" not in result


def test_same_identity_in_two_sections_is_reported_separately(monkeypatch):
    # equipment_onts: the same ONT id can name an interface and a loop -- different
    # instances that must be reported separately, each with its section (regression:
    # their outcomes used to be merged under one selector, hiding the absent read).
    case = CASES["equipment_onts:interfaces"]
    full = harness.full_commands(monkeypatch, case)
    device = harness.Device(case["lines"] + case["sibling"], full=full)
    config = harness.merge(case["config"], {"loops": [{"ont_idx": "1/1/5/1/3"}]})
    result = harness.gathered(monkeypatch, case, config, device)
    assert not result.get("failed"), result
    by_key = dict(((o["section"], o["selector"]), o) for o in harness.outcomes(result))
    assert set(by_key) == {("interfaces", "1/1/5/1/3"), ("loops", "1/1/5/1/3")}, by_key
    assert by_key[("interfaces", "1/1/5/1/3")]["existence"] == "present"
    assert by_key[("loops", "1/1/5/1/3")]["command"] == "ok"
    assert by_key[("loops", "1/1/5/1/3")]["existence"] == "confirmed_absent"


def test_failed_bare_detail_probe_fails_carrying_outcomes(monkeypatch):
    # An attribute-free instance is re-checked with 'flat detail'; if that probe
    # fails, the failure must be reported like any other failed read (regression:
    # the probe's exception used to bypass the failure-outcome handling).
    case = CASES["isam_traps:managers"]
    full = harness.full_commands(monkeypatch, case)
    probe = "info configure trap manager 10.0.0.1:162 flat detail"
    device = harness.Device([], full=full, header=True, fail_commands=(probe,))
    result = harness.gathered(monkeypatch, case, case["config"], device)
    assert result.get("failed"), result
    assert "connection to the device was lost" not in result["msg"], result["msg"]
    assert "(connection_error)" in result["msg"] and "10.0.0.1:162" in result["msg"], result["msg"]
    outcomes = harness.outcome_by_selector(result)
    assert set(outcomes) == {"10.0.0.1:162"}, result.get("read_outcomes")
    outcome = outcomes["10.0.0.1:162"]
    assert outcome["section"] == "managers"
    assert outcome["command"] == "failed"
    assert outcome["existence"] == "unknown"
    assert outcome["error_class"] == "connection_error"
    assert probe in device.commands  # the probe ran, then the module failed


def test_sftp_users_sharing_the_ssh_read_get_one_outcome_each(monkeypatch):
    # Regression (PR #9 review): every ssh.sftp_users entry is read through the same
    # ssh node command. The selectors used to overwrite each other and presence was
    # decided from the reply as a whole: gathering [alice, ghost] with only alice on
    # the device reported ghost present and no outcome for alice.
    case = {"module": "isam_system_security"}
    config = {"ssh": {"sftp_users": [{"name": "alice"}, {"name": "ghost"}]}}
    device = harness.Device(["configure system security ssh sftp-user alice auth-type password"])
    result = harness.gathered(monkeypatch, case, config, device)
    assert not result.get("failed"), result
    assert device.commands == ["info configure system security ssh flat"]
    outcomes = harness.outcome_by_selector(result)
    assert set(outcomes) == {"alice", "ghost"}, result.get("read_outcomes")
    assert outcomes["alice"]["existence"] == "present"
    assert outcomes["alice"]["section"] == "ssh.sftp_users"
    # not on the device: unknown (the shared node read is not the device's explicit
    # absence signal for the user), never present
    assert outcomes["ghost"]["existence"] == "unknown"
    assert outcomes["ghost"]["command"] == "ok"
    assert [user["name"] for user in result["gathered"]["ssh"]["sftp_users"]] == ["alice"]


def test_rejected_selector_warns_in_the_module_result(monkeypatch):
    # gathered alone cannot tell a rejected selector from an absent one: the module
    # warns, naming the selector, and does not fail.
    warnings = []
    monkeypatch.setattr(harness.basic.AnsibleModule, "warn", lambda self, msg: warnings.append(msg))
    case = CASES["vlans"]
    full = harness.full_commands(monkeypatch, case)
    device = harness.Device(case["lines"], full=full, reject=True)
    result = harness.gathered(monkeypatch, case, case["config"], device)
    assert not result.get("failed"), result
    assert harness.outcome_by_selector(result)["100"]["command"] == "rejected"
    assert [w for w in warnings if "rejected the read of config 100" in w], warnings
