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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.voice_sip import (
    Isam_voice_sipTemplate,
)


class Isam_voice_sip(ResourceModule):
    """The isam_voice_sip config class."""

    def __init__(self, module):
        super(Isam_voice_sip, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="voice_sip",
            tmplt=Isam_voice_sipTemplate(),
        )
        self.parsers = {
            "registrar": [
                "registrar.server",
                "registrar.port",
                "registrar.realm",
            ],
            "proxy": [
                "proxy.server",
                "proxy.port",
            ],
            "codec": ["codec.priority"],
            "sip_profile": [
                "sip_profile.timer_t1",
                "sip_profile.timer_t2",
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
            want_section = want.get(section)
            have_section = have.get(section)

            if section in ("codec", "sip_profile"):
                wantd = self._index_by_id(want_section or [])
                haved = self._index_by_id(have_section or [])

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
            else:
                if self.state == "deleted":
                    if want_section:
                        self._compare_entry({}, have_section or {}, parsers)
                else:
                    self._compare_entry(want_section or {}, have_section or {}, parsers)

    def _compare_entry(self, want, have, parsers):
        self.compare(parsers=parsers, want=want, have=have)

    def _index_by_id(self, entries):
        result = {}
        for entry in entries or []:
            key = entry.get("priority") if "priority" in entry else entry.get("name")
            if key is not None:
                result[str(key)] = entry
        return result

    def _normalize_config(self, config):
        return deepcopy(config or {})
