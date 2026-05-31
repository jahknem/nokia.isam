# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.mcast_general import (
    Mcast_generalTemplate,
)


class Mcast_general(ResourceModule):
    """The isam_mcast_general config class."""

    def __init__(self, module):
        super(Mcast_general, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="mcast_general",
            tmplt=Mcast_generalTemplate(),
        )
        self.parsers = [
            "admin_state",
            "forward_method",
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

        if self.state == "merged":
            want = dict_merge(have, want)

        if self.state == "deleted":
            want = {}

        if self.state in ["overridden", "deleted"]:
            if "admin_state" not in want and have.get("admin_state") is True:
                self.addcmd({"admin_state": False}, "admin_state")

        if "admin_state" in want and want.get("admin_state") != have.get("admin_state"):
            self.addcmd({"admin_state": want.get("admin_state")}, "admin_state")

        if "forward_method" in want and want.get("forward_method") != have.get("forward_method"):
            self.addcmd({"forward_method": want.get("forward_method")}, "forward_method")
