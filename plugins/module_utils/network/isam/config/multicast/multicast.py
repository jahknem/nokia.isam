# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.multicast import (
    MulticastTemplate,
)


class Multicast(ResourceModule):
    """The isam_multicast config class."""

    def __init__(self, module):
        super(Multicast, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="multicast",
            tmplt=MulticastTemplate(),
        )
        self.parsers = [
            "igmp.mld_snooping",
            "igmp.mld_querier",
            "igmp.igmp_snooping",
            "igmp.igmp_querier",
            "igmp.query_interval",
            "igmp.query_response_interval",
            "igmp.robustness_count",
            "mcast_control.admin_state",
            "mcast_control.max_groups",
            "mcast_control.max_sources",
        ]

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        want = self._normalize(self.want or {})
        have = self._normalize(self.have or {})

        if self.state == "merged":
            want = dict_merge(have, want)

        if self.state == "deleted":
            want = {}

        self._compare_igmp(want.get("igmp", {}), have.get("igmp", {}))
        self._compare_mcast_control(want.get("mcast_control", {}), have.get("mcast_control", {}))

    def _compare_igmp(self, want, have):
        if self.state in ["overridden", "deleted"]:
            for key, negate_val in [("mld_snooping", False), ("mld_querier", False),
                                     ("igmp_snooping", False), ("igmp_querier", False)]:
                if key not in want and have.get(key) is True:
                    self.addcmd({"igmp": {key: negate_val}}, "igmp." + key)

        for key in ("mld_snooping", "mld_querier", "igmp_snooping", "igmp_querier",
                     "query_interval", "query_response_interval", "robustness_count"):
            if key in want and want.get(key) != have.get(key):
                self.addcmd({"igmp": {key: want.get(key)}}, "igmp." + key)

    def _compare_mcast_control(self, want, have):
        if self.state in ["overridden", "deleted"]:
            if "admin_state" not in want and have.get("admin_state") is True:
                self.addcmd({"mcast_control": {"admin_state": False}}, "mcast_control.admin_state")

        for key in ("admin_state", "max_groups", "max_sources"):
            if key in want and want.get(key) != have.get(key):
                self.addcmd({"mcast_control": {key: want.get(key)}}, "mcast_control." + key)

    def _normalize(self, data):
        if not data:
            return {}
        normalized = dict(data)
        if normalized.get("igmp"):
            normalized["igmp"] = dict(normalized["igmp"])
        if normalized.get("mcast_control"):
            normalized["mcast_control"] = dict(normalized["mcast_control"])
        return normalized
