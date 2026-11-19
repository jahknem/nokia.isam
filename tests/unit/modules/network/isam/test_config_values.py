"""Shared recursive comparisons used by system and system_security."""
from copy import deepcopy

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import changed_values, omitted_values


def test_changed_values_preserves_explicit_false_zero_and_atomic_lists():
    want = {"block": {"enabled": False, "timer": 0, "unset": None}, "entries": [1, 2]}
    have = {"block": {"enabled": True, "timer": 30, "unset": "keep"}, "entries": [1]}
    before = deepcopy((want, have))
    assert changed_values(want, have) == {"block": {"enabled": False, "timer": 0}, "entries": [1, 2]}
    assert (want, have) == before


def test_omitted_values_distinguishes_omission_from_false_and_zero():
    want = {"block": {"enabled": False, "timer": 0, "unset": None}}
    have = {"block": {"enabled": True, "timer": 30, "unset": "reset", "empty": None}, "entries": [1]}
    before = deepcopy((want, have))
    assert omitted_values(want, have) == {"block": {"unset": "reset"}, "entries": [1]}
    assert (want, have) == before


def test_nested_type_changes_and_empty_results():
    assert changed_values({"a": {"b": 1}}, {"a": "old"}) == {"a": {"b": 1}}
    assert omitted_values({"a": "new"}, {"a": {"b": 1}}) == {"a": {"b": 1}}
    assert changed_values({"a": {"b": 1}}, {"a": {"b": 1}}) == {}
    assert omitted_values({"a": {"b": 1}}, {"a": {"b": 1}}) == {}
