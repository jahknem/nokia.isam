# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import dict_merge
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.isam_equipment import (
    Isam_equipmentTemplate,
)


class Isam_equipment(ResourceModule):
    """The isam_equipment config class."""

    def __init__(self, module):
        super(Isam_equipment, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="isam_equipment",
            tmplt=Isam_equipmentTemplate(),
        )
        self.parsers = {
            "shelves": ["shelf.planned_type"],
            "slots": ["slot.planned_type", "slot.unlock"],
            "appliques": ["applique.planned_type"],
            "protection_groups": [
                "protection_group.admin_status",
                "protection_group.eps_quenchfactor",
            ],
        }
        self.want = self._normalize_config(self.want)
        self.have = self._normalize_config(self.have)
        self.before = deepcopy(self.have)

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

        for section, parsers in iteritems(self.parsers):
            wantd = self._index_by_id(want.get(section, []))
            haved = self._index_by_id(have.get(section, []))

            if self.state == "merged":
                wantd = dict_merge(haved, wantd)

            if self.state == "deleted":
                haved = {k: v for k, v in iteritems(haved) if k in wantd or not wantd}
                wantd = {}

            if self.state in ["overridden", "deleted"]:
                for key, entry in iteritems(haved):
                    if key not in wantd:
                        self._compare_entry({}, entry, parsers)

            for key, entry in iteritems(wantd):
                self._compare_entry(entry, haved.pop(key, {}), parsers)

    def _compare_entry(self, want, have, parsers):
        self.compare(parsers=parsers, want=want, have=have)

    def _index_by_id(self, entries):
        return {str(entry["id"]): entry for entry in entries or [] if entry.get("id") is not None}

    def _normalize_config(self, config):
        config = deepcopy(config or {})
        for slot in config.get("slots", []) or []:
            admin_state = slot.pop("admin_state", None)
            if admin_state is not None and slot.get("unlock") is None:
                slot["unlock"] = admin_state == "unlocked"
        return config
