# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import ResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.multicast import MulticastTemplate


class Igmp(ResourceModule):
    """Manage only the configure igmp command family."""

    def __init__(self, module):
        super(Igmp, self).__init__(
            empty_fact_val={}, facts_module=Facts(module), module=module,
            resource="igmp", tmplt=MulticastTemplate(),
        )
        self.parsers = [
            "igmp.mcast_svc_context", "igmp.mld_snooping", "igmp.mld_querier",
            "igmp.igmp_snooping", "igmp.igmp_querier", "igmp.query_interval",
            "igmp.query_response_interval", "igmp.robustness_count",
        ]

    def generate_commands(self):
        want = {"igmp": self.want or {}}
        have = {"igmp": self.have or {}}
        if self.state == "merged":
            from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import dict_merge
            want = dict_merge(have, want)
        if self.state == "deleted":
            want = {"igmp": {}}
        if self.state in ["overridden", "replaced", "deleted"]:
            for key in ("mld_snooping", "mld_querier", "igmp_snooping", "igmp_querier"):
                if key not in want["igmp"] and have["igmp"].get(key) is True:
                    self.addcmd({"igmp": {key: False}}, "igmp." + key)
        for key in ("mcast_svc_context", "mld_snooping", "mld_querier", "igmp_snooping",
                    "igmp_querier", "query_interval", "query_response_interval", "robustness_count"):
            if key in want["igmp"] and want["igmp"].get(key) != have["igmp"].get(key):
                self.addcmd({"igmp": {key: want["igmp"].get(key)}}, "igmp." + key)

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result
