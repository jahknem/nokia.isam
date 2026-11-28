# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.utils.utils import dict_merge
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.isam_equipment import (
    EQUIPMENT_FLAG_FIELDS,
    EQUIPMENT_SECTIONS,
    EQUIPMENT_VALUE_FIELDS,
    Isam_equipmentTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import requested_sections

# section -> {field: device default}; a requested default equals an absent value.
_DEFAULTS = {}
for _section, _field, _cli, _default in EQUIPMENT_VALUE_FIELDS:
    _DEFAULTS.setdefault(EQUIPMENT_SECTIONS[_section], {})[_field] = _default
_DEFAULTS.setdefault("shelves", {})["description"] = ""


class Isam_equipment(IsamResourceModule):
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
            "diagnostics_sfp": ["diagnostics_sfp.rssi_prof_id", "diagnostics_sfp.rssi_state"],
            "protection_elements": ["protection_element.redcy_ctrl_status"],
            "racks": ["rack.description"],
            "external_link_assigns": ["external_link_assign.remote"],
            "external_link_hosts": ["external_link_host.direction"],
        }
        for _section, _field, _cli, _default in EQUIPMENT_VALUE_FIELDS:
            self.parsers[EQUIPMENT_SECTIONS[_section]].append(_section + "." + _field)
        for _section, _field, _cli in EQUIPMENT_FLAG_FIELDS:
            self.parsers[EQUIPMENT_SECTIONS[_section]].append(_section + "." + _field)
        self.parsers["shelves"].append("shelf.description")
        self.singleton_parsers = {
            "envbox": ["envbox.enable_supervise"],
            "isam": ["isam.description"],
        }
        self.want = self._normalize_config(self.want)
        self.have = self._normalize_config(self.have)
        self.before = deepcopy(self.have)

    def generate_commands(self):
        want = self.want or {}
        have = self.have or {}
        # deleted with config acts on the named sections only (naming one applique must
        # not unplan the shelf or the slots)
        requested = requested_sections(self._module) if self.state == "deleted" else set()

        for section, parsers in iteritems(self.parsers):
            if requested and section not in requested:
                continue
            wantd = self._index_by_id(want.get(section, []))
            haved = self._index_by_id(have.get(section, []))

            if self.state == "merged":
                wantd = dict_merge(haved, wantd)
            if section in _DEFAULTS:
                wantd = dict((k, self._strip_defaults(section, v)) for k, v in iteritems(wantd))
                haved = dict((k, self._strip_defaults(section, v)) for k, v in iteritems(haved))

            if self.state == "deleted":
                haved = {k: v for k, v in iteritems(haved) if k in wantd or not wantd}
                wantd = {}

            if self.state in ["overridden", "deleted"]:
                for key, entry in iteritems(haved):
                    if key not in wantd:
                        self._compare_planned({}, entry, section, parsers)

            for key, entry in iteritems(wantd):
                self._compare_planned(entry, haved.pop(key, {}), section, parsers)

        for section, parsers in iteritems(self.singleton_parsers):
            if requested and section not in requested:
                continue
            wantd = want.get(section) or {}
            haved = have.get(section) or {}
            if self.state == "merged":
                wantd = dict_merge(haved, wantd)
            if self.state == "deleted":
                self._compare_entry({}, haved, parsers)
            elif self.state == "overridden" and not wantd:
                self._compare_entry({}, haved, parsers)
            else:
                self._compare_entry(wantd, haved, parsers)

    @staticmethod
    def _strip_defaults(section, entry):
        defaults = _DEFAULTS[section]
        return dict((k, v) for k, v in iteritems(entry) if k not in defaults or v != defaults[k])

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
