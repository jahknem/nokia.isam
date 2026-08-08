#
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam_ntp_onts config file.
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ntp_onts import (
    Ntp_ontsTemplate,
)


class Ntp_onts(ResourceModule):
    """
    The isam_ntp_onts config class
    """

    def __init__(self, module):
        super(Ntp_onts, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="ntp_onts",
            tmplt=Ntp_ontsTemplate(),
        )
        self.parsers = [
            "ntp_ont.server",
            "ntp_ont.port",
            "ntp_ont.poll_interval",
            "ntp_ont.enable",
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
        wantd = self._index_by_ont_id(self.want)
        haved = self._index_by_ont_id(self.have)

        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        if self.state == "deleted":
            haved = {
                k: v for k, v in iteritems(haved) if k in wantd or not wantd
            }
            wantd = {}

        if self.state in ["replaced", "overridden", "deleted"]:
            for k, have in iteritems(haved):
                if k not in wantd:
                    self._compare(want={}, have=have)

        for k, want in iteritems(wantd):
            self._compare(want=want, have=haved.pop(k, {}))

    def _compare(self, want, have):
        self.compare(parsers=self.parsers, want=want, have=have)

    def _index_by_ont_id(self, data):
        indexed = {}
        for entry in data or []:
            ont_id = entry.get("ont_id")
            if ont_id:
                indexed[ont_id] = entry
        return indexed
