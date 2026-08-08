# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_bonding import (
    Xdsl_bondingTemplate,
)


class Xdsl_bonding(ResourceModule):
    """The isam_xdsl_bonding config class."""

    def __init__(self, module):
        super(Xdsl_bonding, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="xdsl_bonding",
            tmplt=Xdsl_bondingTemplate(),
        )
        self.parsers = [
            "group_assembly_time",
        ]

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

        if self.state == "deleted":
            want = {}

        self._compare_group_assembly_time(
            want.get("group_assembly_time"),
            have.get("group_assembly_time"),
        )

    def _compare_group_assembly_time(self, want, have):
        if self.state in ["overridden", "deleted"]:
            if have is not None:
                self.commands.append("configure xdsl-bonding no group-assembly-time")
            return

        if self.state == "replaced":
            if want is None and have is not None:
                self.commands.append("configure xdsl-bonding no group-assembly-time")
                return

        if want is not None and want != have:
            self.addcmd({"group_assembly_time": want}, "group_assembly_time")
