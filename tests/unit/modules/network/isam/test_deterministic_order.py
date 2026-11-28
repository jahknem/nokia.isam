# -*- coding: utf-8 -*-
"""The same input produces the same commands in the same order, in every process.

netcommon's dict_merge ordered new keys and merged lists through sets, so the command
order depended on Python's per-process hash seed. NOC fingerprints the commands of a
check and writes only if the re-check is identical; with a random order the apply gate
refused the write (lab, ONT lifecycle 2026-11-28).
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import os
import subprocess
import sys

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.utils.utils import dict_merge

from .module_runner import run_module

ONT = "1/1/7/16/1"
UNI = ONT + "/1/1"
NAMES = ["ont:" + ONT, "uni:" + UNI] + ["vlan-port:%s:%s" % (UNI, vlan) for vlan in ("10", "20", "30", "99")]


def test_dict_merge_keeps_base_order_then_the_new_keys_in_their_order():
    merged = dict_merge({"b": 1, "a": {"x": 1}}, {"z": 1, "a": {"y": 2}, "c": 3, "y": 4})
    assert list(merged) == ["b", "a", "z", "c", "y"]
    assert list(merged["a"]) == ["x", "y"]


def test_dict_merge_lists_are_the_ordered_union():
    assert dict_merge({"l": ["c", "a", "b"]}, {"l": ["d", "a", "e"]})["l"] == ["c", "a", "b", "d", "e"]
    assert dict_merge({"l": [{"id": 1}]}, {"l": [{"id": 2}, {"id": 1}]})["l"] == [{"id": 1}, {"id": 2}]


def test_dict_merge_values_follow_netcommon():
    assert dict_merge({"a": 1, "b": [1], "c": {"x": 1}}, {"a": None, "b": None, "c": None}) == {"a": None, "b": None, "c": None}
    assert dict_merge({"a": 1}, {"a": 2}) == {"a": 2}
    assert dict_merge({"a": {"x": 1}}, {"a": "flat"}) == {"a": "flat"}


def test_dict_merge_is_the_same_under_every_hash_seed():
    code = ("import json; from ansible_collections.nokia.isam.plugins.module_utils.network.isam.utils.utils import dict_merge;"
            "print(json.dumps(list(dict_merge({}, dict((k, 1) for k in %r)))))" % (NAMES,))
    results = set()
    for seed in ("1", "2", "3", "4", "5", "6"):
        env = dict(os.environ, PYTHONHASHSEED=seed, PYTHONPATH=os.pathsep.join(sys.path))
        results.add(subprocess.check_output([sys.executable, "-c", code], env=env).strip())
    assert len(results) == 1
    assert json.loads(results.pop()) == NAMES


def _ports(commands, prefix):
    return [command.split()[3] for command in commands if command.startswith(prefix)]


def test_merged_interfaces_follow_the_order_given(monkeypatch):
    config = [{"name": name, "admin_up": True} for name in NAMES]
    result = run_module(monkeypatch, "isam_interfaces", {"state": "merged", "config": config})
    assert not result.get("failed"), result.get("msg")
    assert _ports(result["commands"], "configure interface port ") == NAMES


def test_merged_qos_interfaces_follow_the_order_given(monkeypatch):
    names = [UNI, "ont:" + ONT, "1/1/7/16/2/1/1", "ont:1/1/7/16/2", "1/1/7/16/3/1/1", "ont:1/1/7/16/3"]
    config = [{"name": name, "scheduler_node": "name:NGLT_Default"} for name in names]
    result = run_module(monkeypatch, "isam_qos_interfaces", {"state": "merged", "config": config})
    assert not result.get("failed"), result.get("msg")
    assert _ports(result["commands"], "configure qos interface ") == names
