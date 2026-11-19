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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import requested_sections
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
        requested = requested_sections(self._module) if self.state == "deleted" else set()

        for section, parsers in iteritems(self.parsers):
            if requested and section not in requested:
                continue
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
                        self._compare_planned({}, entry, section, parsers)

            for key, entry in iteritems(wantd):
                self._compare_planned(entry, haved.pop(key, {}), section, parsers)

    def _compare_entry(self, want, have, parsers):
        self.compare(parsers=parsers, want=want, have=have)

    def _compare_planned(self, want, have, section, parsers):
        """Shelves, slots and appliques (lab ISAM): the type of a planned entry cannot be
        changed ("needs to be unplanned first", EQPT MGT error 40), and an unplanned entry
        takes no other settings ("not yet planned", error 1)."""
        wtype, htype = want.get("planned_type"), have.get("planned_type")
        if wtype and htype and wtype != htype and self.state != "deleted":
            self._module.fail_json(msg="%s %s is planned as %s; the device only plans an unplanned %s. Unplan it "
                                       "first with state deleted (this removes the configuration on it), then plan %s"
                                       % (section.rstrip("s"), want.get("id"), htype, section.rstrip("s"), wtype))
        if htype and not wtype:
            # unplanning removes everything on it; nothing else is accepted afterwards
            self.compare(parsers=[p for p in parsers if p.endswith(".planned_type")], want=want, have=have)
            return
        self._compare_entry(want, have, parsers)

    def _index_by_id(self, entries):
        return {str(entry["id"]): entry for entry in entries or [] if entry.get("id") is not None}

    def _normalize_config(self, config):
        config = deepcopy(config or {})
        for slot in config.get("slots", []) or []:
            admin_state = slot.pop("admin_state", None)
            if admin_state is not None and slot.get("unlock") is None:
                slot["unlock"] = admin_state == "unlocked"
        return config
