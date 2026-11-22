"""Shared harness for targeted gathering tests (state gathered with config).

A case drives the real module and parser against a fake device answering
``info configure <path> ... flat`` from flat configuration lines:

    "resource:label": {
        "module": "isam_xdsl_lines",          # module under plugins/modules
        "config": [{"name": "1/1/1/1"}],      # names the target instance(s)
        "lines": [...],                       # device lines of the target
        "sibling_config": [{"name": "1/1/1/2"}],
        "sibling": [...],                     # device lines of a neighbour instance
        "marker": "1/1/1/1",                  # appears in the gathered target
        "sibling_marker": "1/1/1/2",          # appears in the gathered neighbour
        "answer": None,                       # optional, see Device
    }

The resource is the part before the colon (TARGETED_GATHER key).
"""
import importlib
import re
import sys

import pytest
from ansible.module_utils import basic

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.targeted import TARGETED_GATHER
from .isam_module import set_module_args


class _ModuleDone(BaseException):
    """Raised by the patched exit_json/fail_json.

    It inherits BaseException (like the real AnsibleModule.exit_json/fail_json, which
    raise SystemExit) so it is NOT swallowed by an ``except Exception`` in the read path
    -- a module that has already failed (e.g. a targeted read carrying read_outcomes)
    must not be re-wrapped by a downstream handler.
    """

    def __init__(self, result):
        super(_ModuleDone, self).__init__()
        self.result = result

_COMMAND = re.compile(r"^info configure (.*?)(?:\s+detail)?(?:\s+flat)?(?:\s+detail)?$")


class Device:
    """Answers 'info configure <path> [flat] [detail]' from flat lines.

    A command without matching lines is an absent instance ("instance does not
    exist"), except the whole-resource commands in ``full``, which are just empty.

    ``fail`` makes every command raise a connection error; ``reject`` makes the
    targeted commands raise the device's selector rejection ("Error : invalid
    token"); ``header`` makes the targeted commands answer with only the header
    (echo + '#---'), like an instance without configured attributes. Whole-resource
    commands in ``full`` are unaffected by reject/header.

    For output that is not flat, a case gives ``answer(command, lines)``: the reply
    text, or None for "nothing matches" (then the same absent/empty rule applies).
    """

    def __init__(self, lines, full=(), fail=False, answer=None, reject=False, header=False):
        self.lines, self.full, self.fail, self.answer, self.commands = lines, full, fail, answer, []
        self.reject, self.header = reject, header

    def get(self, command, *args, **kwargs):
        self.commands.append(command)
        if self.fail:
            raise Exception("Error : connection to the device was lost")
        if self.reject and command not in self.full:
            raise Exception("Error : invalid token")
        if self.header and command not in self.full:
            return "echo %s\n#----------------------------------------\n" % command
        if self.answer is not None:
            reply = self.answer(command, self.lines)
            if reply is None and command not in self.full:
                raise Exception("Error : instance does not exist")
            return reply or ""
        match = _COMMAND.match(command)
        assert match, command
        prefix = "configure " + match.group(1)
        hits = [line for line in self.lines if line == prefix or line.startswith(prefix + " ")]
        if not hits and command not in self.full:
            raise Exception("Error : instance does not exist")
        return "\n".join(hits) + "\n"

    def edit_config(self, *args, **kwargs):
        raise AssertionError("gathered must not change anything")


def gathered(monkeypatch, case, config, device):
    module = importlib.import_module("ansible_collections.nokia.isam.plugins.modules." + case["module"])
    importlib.import_module("ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts")

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
        args = {"state": "gathered"}
        if config is not None:
            args["config"] = config
        set_module_args(args, True)
        with pytest.raises(_ModuleDone) as result:
            module.main()
        return result.value.result


def merge(first, second):
    """Both configs in one: lists concatenated, dicts merged per key."""
    if isinstance(first, list):
        return first + second
    merged = dict(first)
    for key, value in second.items():
        merged[key] = merge(merged[key], value) if key in merged else value
    return merged


def named_sections(config, prefix=""):
    """Instance lists a config names: "config", or (dotted) keys holding lists."""
    if isinstance(config, list):
        return {"config"}
    found = set()
    for key, value in config.items():
        if isinstance(value, list):
            found.add(prefix + key)
        elif isinstance(value, dict):
            found |= named_sections(value, prefix + key + ".")
    return found


def resource_of(name):
    return name.split(":")[0]


def check_coverage(cases):
    """Every instance list in TARGETED_GATHER has a case, and cases only name such lists."""
    covered = {}
    for name, case in cases.items():
        covered.setdefault(resource_of(name), set()).update(named_sections(case["config"]))
    expected = {resource: set(sections) for resource, sections in TARGETED_GATHER.items()}
    assert covered == expected


def full_commands(monkeypatch, case):
    """Commands of the whole-resource read (on an empty device)."""
    device = Device([], full=_AllFull(), answer=case.get("answer"))
    gathered(monkeypatch, case, None, device)
    return set(device.commands)


class _AllFull(set):
    def __contains__(self, item):
        return True


def text(result):
    return repr(result.get("gathered"))


def outcomes(result):
    """The sanitized per-selector read_outcomes of a targeted gathered read ([] if none)."""
    return (result.get("read_outcomes") or {}).get("outcomes") or []


def outcome_by_selector(result):
    """The read_outcomes of a result keyed by selector ({} if the result has none)."""
    return dict((o.get("selector"), o) for o in outcomes(result))


def assert_outcomes(result, axis, value):
    """A targeted gathered read reports one outcome per addressed instance, on ``axis``
    (existence or command), all classified as ``value``."""
    got = outcomes(result)
    assert got, "expected read_outcomes for a targeted gathered read: %r" % result
    assert all(o.get(axis) == value for o in got), result.get("read_outcomes")
    # sanitized: no raw device text in any outcome
    import json
    assert "does not exist" not in json.dumps(result.get("read_outcomes"))


def run_only_named(monkeypatch, case):
    full = full_commands(monkeypatch, case)
    device = Device(case["lines"] + case["sibling"], full=full, answer=case.get("answer"))
    result = gathered(monkeypatch, case, case["config"], device)
    assert not result.get("failed"), result
    assert device.commands and not set(device.commands) & full, (device.commands, full)
    assert case["marker"] in text(result), result
    assert case["sibling_marker"] not in text(result), result
    assert not any(case["sibling_marker"] in command for command in device.commands), device.commands


def run_group(monkeypatch, case):
    full = full_commands(monkeypatch, case)
    device = Device(case["lines"] + case["sibling"], full=full, answer=case.get("answer"))
    result = gathered(monkeypatch, case, merge(case["config"], case["sibling_config"]), device)
    assert not result.get("failed"), result
    assert not set(device.commands) & full, device.commands
    assert case["marker"] in text(result) and case["sibling_marker"] in text(result), result


def run_absent(monkeypatch, case):
    full = full_commands(monkeypatch, case)
    result = gathered(monkeypatch, case, case["config"], Device([], full=full, answer=case.get("answer")))
    assert not result.get("failed"), result
    assert case["marker"] not in text(result), result


def run_errors_fail(monkeypatch, case):
    result = gathered(monkeypatch, case, case["config"], Device([], fail=True, answer=case.get("answer")))
    assert result.get("failed"), result


def run_whole(monkeypatch, case):
    full = full_commands(monkeypatch, case)
    device = Device(case["lines"] + case["sibling"], full=full, answer=case.get("answer"))
    result = gathered(monkeypatch, case, None, device)
    assert not result.get("failed"), result
    assert set(device.commands) <= full, device.commands
    assert case["marker"] in text(result) and case["sibling_marker"] in text(result), result
