# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.dhcp_server import (
    Isam_dhcp_serverTemplate,
)


class Isam_dhcp_server(ResourceModule):
    """The isam_dhcp_server config class."""

    def __init__(self, module):
        super(Isam_dhcp_server, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="isam_dhcp_server",
            tmplt=Isam_dhcp_serverTemplate(),
        )
        self.parsers = [
            "start_addr",
            "end_addr",
            "subnet_mask",
            "lease_time",
            "restart",
        ]
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

        if self.state == "merged":
            want = {k: v for k, v in want.items() if v is not None}
            for key, value in have.items():
                if key not in want:
                    want[key] = value

        if self.state == "deleted":
            want = {}

        self.compare(parsers=self.parsers, want=want, have=have)

    def _normalize_config(self, config):
        return deepcopy(config or {})
