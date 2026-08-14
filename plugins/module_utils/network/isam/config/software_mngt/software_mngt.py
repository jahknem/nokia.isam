# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

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
            "database.backup_options",
            "database.auto_backup_interval",
            "oswp.options",
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
            requested_oswp = want.get("oswp", [])
            if requested_oswp:
                have["oswp"] = [
                    item for item in have.get("oswp", [])
                    if str(item["id"]) in {str(entry["id"]) for entry in requested_oswp}
                ]
            want = {"oswp": requested_oswp}

        self._compare_database(want.get("database", {}), have.get("database", {}))
        self._compare_oswp(want.get("oswp", {}), have.get("oswp", {}))
        self._compare_sw_replacement_mode(want.get("sw_replacement_mode", {}), have.get("sw_replacement_mode", {}))

    def _compare_database(self, want, have):
        for key in ("version", "url"):
            if key in want and want.get(key) != have.get(key):
                self.addcmd({"database": {key: want.get(key)}}, "database." + key)
        if any(key in want and want.get(key) != have.get(key) for key in ("backup", "backupv6")):
            self.addcmd({"database": want}, "database.backup_options")
        if "auto_backup_interval" in want and want.get("auto_backup_interval") != have.get("auto_backup_interval"):
            self.addcmd({"database": want}, "database.auto_backup_interval")
        # NOTE: database.version and database.url have no no-form in the
        # template (no `negate` in getval, no `'no ' if ...` in setval), so
        # they cannot be negated for replaced/overridden states.

    def _compare_oswp(self, want, have):
        want_by_id = {str(item["id"]): item for item in want or []}
        have_by_id = {str(item["id"]): item for item in have or []}

        if self.state in ["overridden", "deleted"]:
            for key, item in have_by_id.items():
                if key not in want_by_id or self.state == "deleted":
                    self.addcmd(item, "oswp.options", negate=True)

        if self.state == "deleted":
            return

        for key, item in want_by_id.items():
            if item != have_by_id.get(key):
                self.addcmd(item, "oswp.options")
            if "admin_state" in item and item["admin_state"] != have_by_id.get(key, {}).get("admin_state"):
                self.addcmd({"id": item["id"], "admin_state": item["admin_state"]}, "oswp.admin_state")

    def _compare_sw_replacement_mode(self, want, have):
        if "mode" in want and want.get("mode") != have.get("mode"):
            self.addcmd({"sw_replacement_mode": {"mode": want.get("mode")}}, "sw_replacement_mode.mode")
        # NOTE: sw_replacement_mode.mode has no no-form in the template (no
        # `negate` in getval, no `'no ' if ...` in setval), so it cannot be
        # negated for replaced/overridden states.

    def _normalize(self, data):
        if not data:
            return {}
        normalized = dict(data)
        if normalized.get("database"):
            normalized["database"] = dict(normalized["database"])
        if normalized.get("oswp"):
            normalized["oswp"] = [dict(item) for item in normalized["oswp"]]
        if normalized.get("sw_replacement_mode"):
            normalized["sw_replacement_mode"] = dict(normalized["sw_replacement_mode"])
        return normalized
