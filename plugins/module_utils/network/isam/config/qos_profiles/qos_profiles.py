# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_profiles import (
    Qos_profilesTemplate,
)


class Qos_profiles(ResourceModule):
    """The isam_qos_profiles config class."""

    def __init__(self, module):
        super(Qos_profiles, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="qos_profiles",
            tmplt=Qos_profilesTemplate(),
        )
        self.parsers = list(Qos_profilesTemplate._FIELDS)

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    @staticmethod
    def _key(entry):
        return "{0}:{1}".format(entry["profile_type"], entry["name"])

    def generate_commands(self):
        wantd = {self._key(entry): entry for entry in self.want}
        haved = {self._key(entry): entry for entry in self.have}

        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        if self.state == "deleted":
            haved = {k: v for k, v in iteritems(haved) if k in wantd or not wantd}
            wantd = {}

        if self.state in ["overridden", "deleted"]:
            for key, have in iteritems(deepcopy(haved)):
                if key not in wantd:
                    self._compare(want={}, have=have)

        for key, want in iteritems(wantd):
            self._compare(want=want, have=haved.pop(key, {}))
        self.commands = list(dict.fromkeys(self.commands))

    def _compare(self, want, have):
        self.compare(parsers=self.parsers, want=want, have=have)
