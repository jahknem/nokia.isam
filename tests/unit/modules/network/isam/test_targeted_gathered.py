"""Targeted gathering for every instance list in TARGETED_GATHER.

``state: gathered`` with ``config`` reads only the named instances (one or several);
without ``config`` the whole resource, as before. Cases live in targeted_cases_*.py,
the checks in targeted_harness.py.
"""
import importlib
import pathlib

import pytest

from . import targeted_harness as harness

CASES = {}
for _path in sorted(pathlib.Path(__file__).parent.glob("targeted_cases_*.py")):
    _cases = importlib.import_module("." + _path.stem, __package__).CASES
    assert not set(_cases) & set(CASES), _path
    CASES.update(_cases)
from . import contract_registry as _registry
NAMES = sorted(name for name in CASES if _registry.case_in_scope(name))


def test_every_instance_list_has_a_case():
    scoped_keys = [name for name in CASES if _registry.case_in_scope(name)]
    required = {harness.resource_of(name) for name in scoped_keys}
    harness.check_coverage(
        {name: CASES[name] for name in scoped_keys},
        expected={r: set(sections) for r, sections in harness.TARGETED_GATHER.items() if r in required})


@pytest.mark.parametrize("name", NAMES)
def test_gathered_with_config_reads_only_the_named_instances(monkeypatch, name):
    harness.run_only_named(monkeypatch, CASES[name])


@pytest.mark.parametrize("name", NAMES)
def test_several_named_instances_are_read_together(monkeypatch, name):
    harness.run_group(monkeypatch, CASES[name])


@pytest.mark.parametrize("name", NAMES)
def test_absent_instances_are_simply_not_gathered(monkeypatch, name):
    harness.run_absent(monkeypatch, CASES[name])


@pytest.mark.parametrize("name", NAMES)
def test_other_device_errors_fail(monkeypatch, name):
    harness.run_errors_fail(monkeypatch, CASES[name])


@pytest.mark.parametrize("name", NAMES)
def test_without_config_the_whole_resource_is_read(monkeypatch, name):
    harness.run_whole(monkeypatch, CASES[name])


@pytest.mark.parametrize("name", [n for n in ["ani_onts", "ntp_onts", "alarm:custom_profiles", "qos_profiles"] if _registry.case_in_scope(n)])
def test_a_bare_header_reply_is_not_returned(monkeypatch, name):
    """Real device form: unset and non-existing instances both answer only '#---'/'echo'.

    They cannot be told apart from a single read, so neither is returned.
    """
    case = CASES[name]
    entry = case["config"][0] if isinstance(case["config"], list) else case["config"]["custom_profiles"][0]
    parts = [str(value) for value in entry.values()]

    class BareHeader(harness.Device):
        def get(self, command, *args, **kwargs):
            self.commands.append(command)
            if all(part in command for part in parts):
                return "#-------------------------------------------------------------------------------\n"
            return super().get(command, *args, **kwargs)

    device = BareHeader(case["sibling"], full=harness.full_commands(monkeypatch, case))
    result = harness.gathered(monkeypatch, case, case["config"], device)
    assert not result.get("failed"), result
    assert case["marker"] not in harness.text(result), result
    assert case["sibling_marker"] not in harness.text(result), result
