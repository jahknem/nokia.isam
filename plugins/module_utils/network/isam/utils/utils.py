# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# utils

from copy import deepcopy

try:
    from collections.abc import Mapping
except ImportError:  # pragma: no cover - Python 2
    from collections import Mapping


def _ordered_union(first, second):
    """Items of first, then those of second not yet seen (equality, keeps order)."""
    out = []
    for item in list(first) + list(second):
        if item not in out:
            out.append(item)
    return out


def dict_merge(base, other):
    """netcommon's dict_merge with a deterministic result.

    netcommon adds the keys only in other through a set difference and merges scalar
    lists through a set, so the order of instances, and with it the order of the
    commands a module sends, changed with Python's per-process hash seed. The same
    change set then produced a different command list on every run (NOC's apply
    gate refused the write because the re-check differed from the approved check).
    Here: base's keys in base's order, then other's new keys in other's order; lists
    as the ordered union. Values follow netcommon's rules otherwise.
    """
    if not isinstance(base, dict):
        raise AssertionError("`base` must be of type <dict>")
    if not isinstance(other, dict):
        raise AssertionError("`other` must be of type <dict>")

    combined = {}
    for key, value in deepcopy(base).items():
        if key not in other:
            combined[key] = value
            continue
        item = other.get(key)
        if item is None:
            combined[key] = item
        elif isinstance(value, dict):
            combined[key] = dict_merge(value, item) if isinstance(item, Mapping) else item
        elif isinstance(value, list):
            combined[key] = _ordered_union(value, item)
        else:
            combined[key] = item
    for key, value in other.items():
        if key not in base:
            combined[key] = value
    return combined
