# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.software_mngt import (
    Software_mngtTemplate,
)


class Software_mngt(ResourceModule):
    """The isam_software_mngt config class."""

    def __init__(self, module):
        super(Software_mngt, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="software_mngt",
            tmplt=Software_mngtTemplate(),
        )
        self.parsers = [
            "database.version",
            "database.url",
            "oswp.admin_state",
            "sw_replacement_mode.mode",
        ]

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        want = self._normalize(self.want or {})
        have = self._normalize(self.have or {})

        if self.state == "merged":
            want = dict_merge(have, want)

        if self.state == "deleted":
            want = {}

        self._compare_database(want.get("database", {}), have.get("database", {}))
        self._compare_oswp(want.get("oswp", {}), have.get("oswp", {}))
        self._compare_sw_replacement_mode(want.get("sw_replacement_mode", {}), have.get("sw_replacement_mode", {}))

    def _compare_database(self, want, have):
        for key in ("version", "url"):
            if key in want and want.get(key) != have.get(key):
                self.addcmd({"database": {key: want.get(key)}}, "database." + key)

    def _compare_oswp(self, want, have):
        if self.state in ["overridden", "deleted"]:
            if "admin_state" not in want and have.get("admin_state") is True:
                self.addcmd({"oswp": {"admin_state": False}}, "oswp.admin_state")

        if "admin_state" in want and want.get("admin_state") != have.get("admin_state"):
            self.addcmd({"oswp": {"admin_state": want.get("admin_state")}}, "oswp.admin_state")

    def _compare_sw_replacement_mode(self, want, have):
        if "mode" in want and want.get("mode") != have.get("mode"):
            self.addcmd({"sw_replacement_mode": {"mode": want.get("mode")}}, "sw_replacement_mode.mode")

    def _normalize(self, data):
        if not data:
            return {}
        normalized = dict(data)
        if normalized.get("database"):
            normalized["database"] = dict(normalized["database"])
        if normalized.get("oswp"):
            normalized["oswp"] = dict(normalized["oswp"])
        if normalized.get("sw_replacement_mode"):
            normalized["sw_replacement_mode"] = dict(normalized["sw_replacement_mode"])
        return normalized
