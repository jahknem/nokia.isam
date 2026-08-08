# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.interface_alarms import (
    Interface_alarmsTemplate,
)


class Interface_alarms(ResourceModule):
    """The isam_interface_alarms config class."""

    def __init__(self, module):
        super(Interface_alarms, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="interface_alarms",
            tmplt=Interface_alarmsTemplate(),
        )
        self.parsers = ["default_severity"]

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        wantd = self._index_by_id(self.want)
        haved = self._index_by_id(self.have)

        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        if self.state == "deleted":
            haved = {k: v for k, v in iteritems(haved) if k in wantd or not wantd}
            wantd = {}

        if self.state in ["replaced", "overridden", "deleted"]:
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
            key = entry.get("name")
            if key:
                indexed[key] = dict(entry)
        return indexed
