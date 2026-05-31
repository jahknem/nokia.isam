# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.li_vlan import (
    Li_vlanTemplate,
)


class Li_vlan(ResourceModule):
    """The isam_li_vlan config class."""

    def __init__(self, module):
        super(Li_vlan, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="li_vlan",
            tmplt=Li_vlanTemplate(),
        )
        self.parsers = [
            "vlan_id",
        ]

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        want = self._normalize(self.want)
        have = self._normalize(self.have)

        if self.state == "merged":
            want = dict_merge(have, want)

        if self.state == "deleted":
            want = {}

        self._compare(want, have)

    def _compare(self, want, have):
        for key in self.parsers:
            if key in want and want.get(key) != have.get(key):
                self.addcmd({key: want.get(key)}, key)

    def _normalize(self, data):
        if not data:
            return {}
        normalized = dict(data)
        if "vlan-id" in normalized and "vlan_id" not in normalized:
            normalized["vlan_id"] = normalized.pop("vlan-id")
        return normalized
