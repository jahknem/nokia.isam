# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import dict_merge
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.system import (
    Isam_systemTemplate,
)


class Isam_system(ResourceModule):
    """The isam_system config class."""

    def __init__(self, module):
        super(Isam_system, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="system",
            tmplt=Isam_systemTemplate(),
        )
        self.parsers = {
            "id": ["id.name", "id.location", "id.contact"],
            "security": ["security.ssh", "security.telnet", "security.snmp"],
            "sntp": ["sntp.server", "sntp.port", "sntp.poll_interval"],
            "syslog": ["syslog.server", "syslog.facility", "syslog.severity"],
            "sync_if_timing": ["sync_if_timing.mode", "sync_if_timing.source"],
            "transaction": ["transaction.timeout"],
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

        for section, parsers in self.parsers.items():
            want_section = want.get(section)
            have_section = have.get(section)

            if self.state == "merged":
                if want_section is not None:
                    want_section = dict_merge(have_section or {}, want_section)

            if self.state == "deleted":
                if want_section is not None:
                    have_section = have_section
                    want_section = {}
                else:
                    have_section = {}

            if self.state in ["overridden", "deleted"]:
                if have_section and not want_section:
                    self._compare_section({}, have_section, parsers)

            if want_section is not None:
                self._compare_section(want_section, have_section or {}, parsers)

    def _compare_section(self, want, have, parsers):
        self.compare(parsers=parsers, want=want, have=have)

    def _normalize_config(self, config):
        return deepcopy(config or {})
