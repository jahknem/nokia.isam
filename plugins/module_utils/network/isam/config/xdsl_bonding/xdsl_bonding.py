# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_bonding import (
    Xdsl_bondingTemplate,
)

# Device defaults: a requested default equals an absent value (detail mode prints them as 'no <attr>').
_GROUP_DEFAULTS = {"group_profile": "none", "group_rtx_profile": "none", "up": False}
_VECT_FALLBACK_DEFAULTS = {"group_profile": "group-level", "group_rtx_profile": "group-level"}
_PTM_INIT_MODE_DEFAULT = "mode1"


class Xdsl_bonding(IsamResourceModule):
    """The isam_xdsl_bonding config class."""

    def __init__(self, module):
        super(Xdsl_bonding, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="xdsl_bonding",
            tmplt=Xdsl_bondingTemplate(),
        )
        self.parsers = [
            "group_assembly_time",
        ]
        self.list_parsers = {
            "groups": ("group_id", ["group.group_profile", "group.group_rtx_profile", "group.up"]),
            "boards": ("board_id", ["board.vect_fallback.group_profile", "board.vect_fallback.group_rtx_profile"]),
        }

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        want = self.want or {}
        have = self.have or {}

        if self.state == "deleted":
            requested = want
            want = {}
        else:
            requested = None

        if not requested or "group_assembly_time" in requested:
            self._compare_group_assembly_time(
                want.get("group_assembly_time"),
                have.get("group_assembly_time"),
            )
        if not requested or "ptm_init_mode" in requested:
            self._compare_ptm_init_mode(want, have)
        for section, (key, parsers) in iteritems(self.list_parsers):
            if requested and section not in requested:
                continue
            self._compare_list(section, key, parsers, want, have, requested)

    def _compare_group_assembly_time(self, want, have):
        if self.state == "deleted":
            if have is not None:
                self.commands.append("configure xdsl-bonding no group-assembly-time")
            return

        if self.state in ["replaced", "overridden"]:
            if want is None and have is not None:
                self.commands.append("configure xdsl-bonding no group-assembly-time")
                return

        if want is not None and want != have:
            self.addcmd({"group_assembly_time": want}, "group_assembly_time")

    def _compare_ptm_init_mode(self, want, have):
        wanted = want.get("ptm_init_mode")
        current = have.get("ptm_init_mode")
        if wanted is None and self.state == "merged":
            return
        wanted = None if wanted == _PTM_INIT_MODE_DEFAULT else wanted
        current = None if current == _PTM_INIT_MODE_DEFAULT else current
        if wanted == current:
            return
        # ptm-init-mode is a parameter of the group-assembly-time command, which needs the time itself.
        assembly_time = want.get("group_assembly_time")
        if assembly_time is None or self.state in ["overridden", "deleted"]:
            assembly_time = have.get("group_assembly_time")
        if assembly_time is None:
            assembly_time = 0
        data = {"group_assembly_time": assembly_time, "ptm_init_mode": wanted or current}
        self.addcmd(data, "ptm_init_mode", wanted is None)

    def _compare_list(self, section, key, parsers, want, have, requested):
        wantd = self._index(want.get(section), key)
        haved = self._index(have.get(section), key)

        if self.state == "merged":
            wantd = dict_merge(haved, wantd)
        wantd = {k: _strip_defaults(v) for k, v in iteritems(wantd)}
        haved = {k: _strip_defaults(v) for k, v in iteritems(haved)}

        if self.state == "deleted":
            names = self._index((requested or {}).get(section), key)
            haved = {k: v for k, v in iteritems(haved) if k in names or not names}

        if self.state in ["overridden", "deleted"]:
            for name, entry in iteritems(haved):
                if name not in wantd:
                    self.compare(parsers=parsers, want={key: name}, have=entry)

        for name, entry in iteritems(wantd):
            self.compare(parsers=parsers, want=entry, have=haved.get(name, {key: name}))

    @staticmethod
    def _index(entries, key):
        indexed = {}
        for entry in entries or []:
            if entry.get(key) is None:
                continue
            entry = deepcopy(entry)
            indexed[str(entry[key])] = entry
        return indexed


def _strip_defaults(entry):
    for name, default in iteritems(_GROUP_DEFAULTS):
        if entry.get(name) == default:
            entry.pop(name)
    fallback = entry.get("vect_fallback")
    if isinstance(fallback, dict):
        entry["vect_fallback"] = {
            name: value for name, value in iteritems(fallback)
            if value is not None and value != _VECT_FALLBACK_DEFAULTS.get(name)
        }
    return entry
