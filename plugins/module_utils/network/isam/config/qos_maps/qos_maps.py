# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_maps import (
    Qos_mapsTemplate,
)


class Qos_maps(IsamResourceModule):
    """The isam_qos_maps config class."""

    IDENTITIES = {"tc_map_dot1p": "dot1p", "dscp_map_dot1p": "dscp",
                  "up_ctrl_pkt": "protocol", "dn_ctrl_pkt": "protocol"}

    def __init__(self, module):
        super(Qos_maps, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="qos_maps",
            tmplt=Qos_mapsTemplate(),
        )

    @classmethod
    def _key(cls, entry, field):
        return entry.get(cls.IDENTITIES[field])

    def _add_commands(self, entries, field):
        self._map_commands(entries, field)

    def _del_commands(self, entries, field):
        self._map_commands(entries, field, remove=True)

    def _map_commands(self, entries, field, remove=False):
        # The four map families have the same identity/diff mechanics; their
        # different CLI forms remain in the template's explicit renderers.
        if field not in self.IDENTITIES:
            raise ValueError("unknown QoS map: %s" % field)
        renderer = getattr(Qos_mapsTemplate, "_render_%s%s" % ("no_" if remove else "", field))
        for entry in entries or []:
            self.commands.append(renderer(entry))

    def generate_commands(self):
        # Reconciliation builds merged entries without modifying the user's request.
        wantd = dict(self.want or {})
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

        # deleted: without config every entry; with config only the named entries of the
        # named maps. The device's entry is rendered, so naming the identity is enough.
        if self.state == "deleted":
            named = dict((field, set(self._key(e, field) for e in wantd.get(field) or []))
                         for field in wantd if wantd.get(field))
            for field in list(haved.keys()):
                if named and field not in named:
                    continue
                self._del_commands([e for e in haved.get(field) or []
                                    if not named or self._key(e, field) in named[field]], field)
            self.commands = list(dict.fromkeys(self.commands))
            return

        # overridden: remove entire fields present in have but absent from want
        if self.state == "overridden":
            for field in haved:
                if field not in wantd:
                    self._del_commands(haved.get(field), field)

        # replaced/overridden: for each field in want, delete sub-entries
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

            if self.state in ("replaced", "overridden"):
                for entry in have_list:
                    if self._key(entry, field) not in want_keys:
                        self._del_commands([entry], field)

            for entry in want_list:
                k = self._key(entry, field)
                have_entry = next((e for e in have_list if self._key(e, field) == k), None)
                if have_entry != entry:
                    self._add_commands([entry], field)

        self.commands = list(dict.fromkeys(self.commands))
