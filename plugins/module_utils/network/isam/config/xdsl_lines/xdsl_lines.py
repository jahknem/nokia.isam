# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam_xdsl_lines config file.
"""

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_lines import (
    Xdsl_linesTemplate,
)


class Xdsl_lines(ResourceModule):
    """The isam_xdsl_lines config class."""

    def __init__(self, module):
        super(Xdsl_lines, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="xdsl_lines",
            tmplt=Xdsl_linesTemplate(),
        )
        self.parsers = [
            "service_profile",
            "spectrum_profile",
            "dpbo_profile",
            "vect_profile",
            "admin_up",
        ]

    def execute_module(self):
        """Execute the module."""
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        """Generate configuration commands from want, have and state."""
        wantd = self._index_by_id(self.want)
        haved = self._index_by_id(self.have)

        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        if self.state == "deleted":
            haved = {k: v for k, v in iteritems(haved) if k in wantd or not wantd}
            wantd = {}

        if self.state in ["overridden", "deleted"]:
            for k, have in iteritems(haved):
                if k not in wantd:
                    self._compare(want={}, have=have)

        for k, want in iteritems(wantd):
            self._compare(want=want, have=haved.pop(k, {}))

    def _compare(self, want, have):
        self.compare(parsers=self.parsers, want=want, have=have)

    @staticmethod
    def _index_by_id(data):
        indexed = {}
        for entry in data or []:
            normalized = dict(entry)
            if "if_index" in normalized and "name" not in normalized:
                normalized["name"] = normalized["if_index"]
            for dashed, underscored in (
                ("service-profile", "service_profile"),
                ("spectrum-profile", "spectrum_profile"),
                ("dpbo-profile", "dpbo_profile"),
                ("vect-profile", "vect_profile"),
                ("admin-up", "admin_up"),
            ):
                if dashed in normalized and underscored not in normalized:
                    normalized[underscored] = normalized[dashed]

            key = normalized.get("name") or normalized.get("if_index")
            if key:
                indexed[key] = normalized
        return indexed
