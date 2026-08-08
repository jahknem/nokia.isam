# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import ResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.multicast import MulticastTemplate


class Mcast_control(ResourceModule):
    """Manage only the configure mcast-control command family."""

    def __init__(self, module):
        super(Mcast_control, self).__init__(
            empty_fact_val={}, facts_module=Facts(module), module=module,
            resource="mcast_control", tmplt=MulticastTemplate(),
        )
        self.parsers = ["mcast_control.mcast_svc_context", "mcast_control.admin_state",
                        "mcast_control.max_groups", "mcast_control.max_sources"]

    def generate_commands(self):
        want = {"mcast_control": self.want or {}}
        have = {"mcast_control": self.have or {}}
        if self.state == "merged":
            from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import dict_merge
            want = dict_merge(have, want)
        if self.state == "deleted":
            want = {"mcast_control": {}}
        if self.state in ["overridden", "replaced", "deleted"] and "admin_state" not in want["mcast_control"]:
            if have["mcast_control"].get("admin_state") is True:
                self.addcmd({"mcast_control": {"admin_state": False}}, "mcast_control.admin_state")
        for key in ("mcast_svc_context", "admin_state", "max_groups", "max_sources"):
            if key in want["mcast_control"] and want["mcast_control"].get(key) != have["mcast_control"].get(key):
                self.addcmd({"mcast_control": {key: want["mcast_control"].get(key)}}, "mcast_control." + key)

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result
