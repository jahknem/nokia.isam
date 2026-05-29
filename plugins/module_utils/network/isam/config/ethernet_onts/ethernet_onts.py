#
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam_ethernet_onts config file.
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ethernet_onts import (
    Ethernet_ontsTemplate,
)


class Ethernet_onts(ResourceModule):
    """
    The isam_ethernet_onts config class
    """

    def __init__(self, module):
        super(Ethernet_onts, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="ethernet_onts",
            tmplt=Ethernet_ontsTemplate(),
        )
        self.parsers = [
            "ont.cust_info",
            "ont.auto_detect",
            "ont.admin_state",
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
        """Generate configuration commands to send based on want, have and state."""
        wantd = self._index_by_uni_idx(self.want)
        haved = self._index_by_uni_idx(self.have)

        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        if self.state == "deleted":
            haved = {
                k: v for k, v in iteritems(haved) if k in wantd or not wantd
            }
            wantd = {}

        if self.state in ["overridden", "deleted"]:
            for k, have in iteritems(haved):
                if k not in wantd:
                    self._compare(want={}, have=have)

        for k, want in iteritems(wantd):
            self._compare(want=want, have=haved.pop(k, {}))

    def _compare(self, want, have):
        self.compare(parsers=self.parsers, want=want, have=have)

    def _index_by_uni_idx(self, data):
        indexed = {}
        for entry in data or []:
            uni_idx = entry.get("uni_idx") or entry.get("name")
            if uni_idx:
                entry["uni_idx"] = uni_idx
                indexed[uni_idx] = entry
        return indexed
