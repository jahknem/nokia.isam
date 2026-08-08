# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_maps import (
    Qos_mapsTemplate,
)


class Qos_maps(ResourceModule):
    """The isam_qos_maps config class."""

    def __init__(self, module):
        super(Qos_maps, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="qos_maps",
            tmplt=Qos_mapsTemplate(),
        )

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    @staticmethod
    def _key(entry, field):
        if field == "tc_map_dot1p":
            return entry.get("dot1p")
        if field == "dscp_map_dot1p":
            return entry.get("dscp")
        return entry.get("protocol")

    def _add_commands(self, entries, field):
        for entry in entries or []:
            if field == "tc_map_dot1p":
                self.commands.append(Qos_mapsTemplate._render_tc_map_dot1p(entry))
            elif field == "dscp_map_dot1p":
                self.commands.append(Qos_mapsTemplate._render_dscp_map_dot1p(entry))
            elif field == "up_ctrl_pkt":
                self.commands.append(Qos_mapsTemplate._render_up_ctrl_pkt(entry))
            elif field == "dn_ctrl_pkt":
                self.commands.append(Qos_mapsTemplate._render_dn_ctrl_pkt(entry))

    def _del_commands(self, entries, field):
        for entry in entries or []:
            if field == "tc_map_dot1p":
                self.commands.append(Qos_mapsTemplate._render_no_tc_map_dot1p(entry))
            elif field == "dscp_map_dot1p":
                self.commands.append(Qos_mapsTemplate._render_no_dscp_map_dot1p(entry))
            elif field == "up_ctrl_pkt":
                self.commands.append(Qos_mapsTemplate._render_no_up_ctrl_pkt(entry))
            elif field == "dn_ctrl_pkt":
                self.commands.append(Qos_mapsTemplate._render_no_dn_ctrl_pkt(entry))

    def generate_commands(self):
        wantd = self.want or {}
        haved = self.have or {}

        # merged: merge want into have so unmentioned entries/fields are preserved
        if self.state == "merged":
            for field in wantd:
                want_list = wantd.get(field) or []
                have_list = haved.get(field) or []
                have_dict = {self._key(e, field): e for e in have_list}
                want_dict = {self._key(e, field): e for e in want_list}
                merged = dict_merge(have_dict, want_dict)
                wantd[field] = list(merged.values())

        # deleted: if want is empty, delete every field and return
        if self.state == "deleted":
            for field in list(haved.keys()):
                if field not in wantd or not wantd:
                    self._del_commands(haved.get(field), field)
            if not wantd:
                self.commands = list(dict.fromkeys(self.commands))
                return

        # overridden/deleted: remove entire fields present in have but absent from want
        if self.state in ["overridden", "deleted"]:
            for field in haved:
                if field not in wantd:
                    self._del_commands(haved.get(field), field)

        # replaced/overridden/deleted: for each field in want, delete sub-entries
        # present in have but absent from want, then add/update entries to match want.
        # For merged the dict_merge above already copied all have entries into wantd
        # so the deletion branch below is a no-op for that state.
        #
        # replaced leaves fields entirely absent from want untouched (no field-level
        # deletion), which is already guaranteed because this loop only processes
        # fields that ARE in wantd.
        for field in wantd:
            want_list = wantd.get(field) or []
            have_list = haved.get(field) or []
            want_keys = {self._key(e, field) for e in want_list}

            if self.state in ("replaced", "overridden", "deleted"):
                for entry in have_list:
                    if self._key(entry, field) not in want_keys:
                        self._del_commands([entry], field)

            for entry in want_list:
                k = self._key(entry, field)
                have_entry = next((e for e in have_list if self._key(e, field) == k), None)
                if have_entry != entry:
                    self._add_commands([entry], field)

        self.commands = list(dict.fromkeys(self.commands))
