# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import dict_merge
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import deleted_targets, requested_sections
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.vlan_global import (
    Isam_vlan_globalTemplate,
)


class Isam_vlan_global(IsamResourceModule):
    """The isam_vlan_global config class."""

    def __init__(self, module):
        super(Isam_vlan_global, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="isam_vlan_global",
            tmplt=Isam_vlan_globalTemplate(),
        )
        self.dict_parsers = {
            "broadcast_frames": [
                "broadcast_frames.priority_policy",
                "broadcast_frames.drop_unknown_multicast",
            ],
            "tpid": [
                "tpid.value",
            ],
            "vmac_address_format": [
                "vmac_address_format.format",
            ],
        }
        self.list_parsers = {
            "priority_regen": [
                "priority_regen",
            ],
        }
        self.want = self._normalize_config(self.want)
        self.have = self._normalize_config(self.have)
        self.before = deepcopy(self.have)

    def generate_commands(self):
        want = self.want or {}
        have = self.have or {}
        # deleted with config acts on the named sections only
        requested = requested_sections(self._module) if self.state == "deleted" else set()

        for section, parsers in iteritems(self.dict_parsers):
            if requested and section not in requested:
                continue
            want_section = want.get(section)
            have_section = have.get(section)

            if self.state == "merged":
                merged = dict_merge(have_section or {}, want_section or {})
                self._compare_entry(merged, have_section or {}, parsers)
            elif self.state == "deleted":
                self._compare_entry({}, have_section or {}, parsers)
            elif self.state in ["replaced", "overridden"]:
                self._compare_entry(want_section or {}, have_section or {}, parsers)
            else:
                self._compare_entry(want_section or {}, have_section or {}, parsers)

        for section, parsers in iteritems(self.list_parsers):
            if requested and section not in requested:
                continue
            wantd = self._index_by_id(want.get(section, []))
            haved = self._index_by_id(have.get(section, []))

            if self.state == "merged":
                wantd = dict_merge(haved, wantd)

            if self.state == "deleted":
                for target, entry in deleted_targets(wantd, haved, ("id",)):
                    # an entry keeping only its id is removed as a whole
                    self._compare_list_entry(target if len(target) > 1 else {}, entry, section, parsers)
                continue

            if self.state == "overridden":
                for key, entry in iteritems(haved):
                    if key not in wantd:
                        self._compare_list_entry({}, entry, section, parsers)

            for key, entry in iteritems(wantd):
                self._compare_list_entry(entry, haved.pop(key, {}), section, parsers)

    def _compare_entry(self, want, have, parsers):
        self.compare(parsers=parsers, want=want, have=have)

    def _compare_list_entry(self, want, have, section, parsers):
        want_wrapped = {section: want} if want else {}
        have_wrapped = {section: have} if have else {}
        self.compare(parsers=parsers, want=want_wrapped, have=have_wrapped)

    def _index_by_id(self, entries):
        return {str(entry["id"]): entry for entry in entries or [] if entry.get("id") is not None}

    def _normalize_config(self, config):
        config = deepcopy(config or {})
        return config
