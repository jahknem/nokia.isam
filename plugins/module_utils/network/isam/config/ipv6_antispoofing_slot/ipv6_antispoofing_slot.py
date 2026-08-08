# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import ResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.ipv6_antispoofing_slot.ipv6_antispoofing_slot import Isam_ipv6_antispoofing_slotFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ipv6_antispoofing_slot import Isam_ipv6_antispoofing_slotTemplate


class Isam_ipv6_antispoofing_slot(ResourceModule):
    def __init__(self, module):
        super(Isam_ipv6_antispoofing_slot, self).__init__(
            empty_fact_val=[], facts_module=Isam_ipv6_antispoofing_slotFacts(module),
            module=module, resource="isam_ipv6_antispoofing_slot", tmplt=Isam_ipv6_antispoofing_slotTemplate(),
        )
        self.want = self._by_name(self.want)
        self.have = self._by_name(self.have)

    @staticmethod
    def _by_name(items):
        return {item["name"]: item for item in (items or [])}

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ("parsed", "gathered"):
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        want = deepcopy(self.want)
        have = deepcopy(self.have)
        if self.state == "merged":
            for name, item in have.items():
                want.setdefault(name, item)
        elif self.state == "deleted":
            want = {name: {} for name in (want or have)}
        elif self.state in ("replaced", "overridden"):
            for name in set(have) - set(want):
                self._add_command(name, None)

        for name, item in want.items():
            current = have.get(name, {})
            if self.state == "deleted":
                if current:
                    self._add_command(name, None)
            elif item.get("bit_len") is not None and item.get("bit_len") != current.get("bit_len"):
                self._add_command(name, item["bit_len"])

    def _add_command(self, name, bit_len):
        if bit_len is None:
            self.commands.append("configure ipv6-antispoofing slot {0} no bit-len".format(name))
        else:
            self.commands.append("configure ipv6-antispoofing slot {0} bit-len {1}".format(name, bit_len))
