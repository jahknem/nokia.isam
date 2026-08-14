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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xstp import (
    XstpTemplate,
)


class Xstp(ResourceModule):
    """The isam_xstp config class."""

    def __init__(self, module):
        super(Xstp, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="xstp",
            tmplt=XstpTemplate(),
        )
        self.parsers = [
            "general.enable_stp",
            "general.region_name",
            "ports.path_cost",
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

        self._compare_general(want.get("general", {}), have.get("general", {}))
        self._compare_ports(want.get("ports", []), have.get("ports", []))

    def _compare_general(self, want, have):
        if self.state in ["overridden", "replaced", "deleted"]:
            if "enable_stp" not in want and have.get("enable_stp") is True:
                self.addcmd({"general": {"enable_stp": False}}, "general.enable_stp")

        if "enable_stp" in want and want.get("enable_stp") != have.get("enable_stp"):
            self.addcmd({"general": {"enable_stp": want.get("enable_stp")}}, "general.enable_stp")

        if "region_name" in want and want.get("region_name") != have.get("region_name"):
            self.addcmd({"general": {"region_name": want.get("region_name")}}, "general.region_name")

    def _compare_ports(self, want, have):
        wantd = self._index_ports(want)
        haved = self._index_ports(have)

        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        if self.state == "deleted":
            haved = {k: v for k, v in iteritems(haved) if k in wantd or not wantd}
            wantd = {}

        if self.state in ["overridden", "deleted"]:
            # The observed port field has no documented no-form; leave unmentioned ports unchanged.
            haved = {k: v for k, v in iteritems(haved) if k in wantd}

        for port, want_entry in iteritems(wantd):
            have_entry = haved.get(port, {})
            if "path_cost" in want_entry and want_entry.get("path_cost") != have_entry.get("path_cost"):
                self.addcmd(want_entry, "ports.path_cost")

    def _normalize(self, data):
        if not data:
            return {}
        normalized = dict(data)
        normalized["general"] = self._normalize_general(normalized.get("general") or {})
        normalized["ports"] = list(self._index_ports(normalized.get("ports") or []).values())
        return normalized

    def _normalize_general(self, general):
        normalized = dict(general)
        if "enable-stp" in normalized and "enable_stp" not in normalized:
            normalized["enable_stp"] = normalized.pop("enable-stp")
        if "region-name" in normalized and "region_name" not in normalized:
            normalized["region_name"] = normalized.pop("region-name")
        return normalized

    def _index_ports(self, ports):
        indexed = {}
        for entry in ports or []:
            normalized = dict(entry)
            if "id" in normalized and "port" not in normalized:
                normalized["port"] = normalized.pop("id")
            if "name" in normalized and "port" not in normalized:
                normalized["port"] = normalized.pop("name")
            if "path-cost" in normalized and "path_cost" not in normalized:
                normalized["path_cost"] = normalized.pop("path-cost")
            port = normalized.get("port")
            if port:
                indexed[port] = normalized
        return indexed
