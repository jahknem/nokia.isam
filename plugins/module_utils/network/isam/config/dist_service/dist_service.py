# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import ResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.dist_service.dist_service import Isam_dist_serviceFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.dist_service import Isam_dist_serviceTemplate


class _DistServiceFactsProvider(object):
    def __init__(self, module):
        self._facts = Facts(module)
        self._resource_facts = Isam_dist_serviceFacts(module)

    def get_facts(self, legacy_facts_type=None, resource_facts_type=None, data=None):
        ansible_facts = {"ansible_network_resources": {}}
        self._resource_facts.populate_facts(self._facts._connection, ansible_facts, data=data)
        return ansible_facts, []


class Isam_dist_service(ResourceModule):
    def __init__(self, module):
        super(Isam_dist_service, self).__init__(
            empty_fact_val=[], facts_module=_DistServiceFactsProvider(module), module=module,
            resource="isam_dist_service", tmplt=Isam_dist_serviceTemplate(),
        )
        self.parsers = ["service_type", "qos_profile"]
        self.before = deepcopy(self.have)

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        want = {entry["name"]: entry for entry in (self.want or [])}
        have = {entry["name"]: entry for entry in (self.have or [])}
        if self.state == "merged":
            for name, item in iteritems(have):
                if name in want:
                    merged = deepcopy(item)
                    merged.update(want[name])
                    want[name] = merged
        if self.state == "deleted":
            if want:
                have = {name: item for name, item in iteritems(have) if name in want}
            want = {}
        if self.state in ["overridden", "deleted"]:
            for name, item in iteritems(have):
                if name not in want:
                    self.compare(parsers=self.parsers, want={}, have=item)
        for name, item in iteritems(want):
            self.compare(parsers=self.parsers, want=item, have=have.get(name, {}))
