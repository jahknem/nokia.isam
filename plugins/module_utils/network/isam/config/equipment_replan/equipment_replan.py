# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.equipment_replan import (
    Equipment_replanTemplate,
)


class Equipment_replan(ResourceModule):
    """The isam_equipment_replan config class."""

    def __init__(self, module):
        super(Equipment_replan, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="equipment_replan",
            tmplt=Equipment_replanTemplate(),
        )
        self.parsers = ["board_auto_replan"]

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
            for k, v in have.items():
                want.setdefault(k, v)

        if self.state == "deleted":
            want = {}

        if self.state in ["overridden", "deleted"]:
            if have and not want:
                self.addcmd(have, "board_auto_replan", negate=True)
                return

        self.compare(parsers=self.parsers, want=want, have=have)
