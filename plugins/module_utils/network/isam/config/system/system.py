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
            "security": ["security.ssh", "security.telnet", "security.snmp", "security.welcome_banner"],
            "sntp": [
                "sntp.server", "sntp.port", "sntp.poll_interval",
                "sntp.server_ip_addr", "sntp.polling_rate", "sntp.enabled",
                "sntp.timezone_offset",
            ],
            "syslog": ["syslog.server", "syslog.facility", "syslog.severity"],
            "sync_if_timing": ["sync_if_timing.mode", "sync_if_timing.source"],
            "loop_id_syntax": [
                "loop_id_syntax.atm_based_dsl",
                "loop_id_syntax.efm_based_dsl",
                "loop_id_syntax.efm_based_pon",
                "loop_id_syntax.efm_based_epon",
                "loop_id_syntax.efm_based_ngpon2",
            ],
            "relay_id_syntax": [
                "relay_id_syntax.atm_based_dsl",
                "relay_id_syntax.efm_based_dsl",
            ],
            "transaction": ["transaction.timeout"],
            "max_lt_link_speed": ["max_lt_link_speed"],
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
            if section == "max_lt_link_speed":
                want_section = (
                    {section: want.get(section)} if section in want else None
                )
                have_section = (
                    {section: have.get(section)} if section in have else None
                )
            else:
                want_section = want.get(section)
                have_section = have.get(section)

            if self.state == "merged":
                if want_section is not None:
                    want_section = dict_merge(have_section or {}, want_section)

            if self.state == "deleted":
                if want_section is not None:
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
