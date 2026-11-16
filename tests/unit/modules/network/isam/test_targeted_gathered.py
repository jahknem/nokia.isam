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
NAMES = sorted(CASES)


def test_every_instance_list_has_a_case():
    harness.check_coverage(CASES)


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
