# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import ResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.dhcp_relay.dhcp_relay import Isam_dhcp_relayFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.dhcp_relay import Isam_dhcp_relayTemplate


class _DhcpRelayFactsProvider(object):
    """Use the normal connection setup without changing the shared fact registry."""

    def __init__(self, module):
        self._facts = Facts(module)
        self._resource_facts = Isam_dhcp_relayFacts(module)

    def get_facts(self, legacy_facts_type=None, resource_facts_type=None, data=None):
        ansible_facts = {"ansible_network_resources": {}}
        self._resource_facts.populate_facts(
            self._facts._connection, ansible_facts, data=data
        )
        return ansible_facts, []


class Isam_dhcp_relay(ResourceModule):
    """The isam_dhcp_relay config class."""

    def __init__(self, module):
        super(Isam_dhcp_relay, self).__init__(
            empty_fact_val=[], facts_module=_DhcpRelayFactsProvider(module), module=module,
            resource="isam_dhcp_relay", tmplt=Isam_dhcp_relayTemplate(),
        )
        self.parsers = ["port_stats", "v6_port_stats"]
        self.before = deepcopy(self.have)

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        wantd = {entry["name"]: entry for entry in (self.want or [])}
        haved = {entry["name"]: entry for entry in (self.have or [])}
        if self.state == "merged":
            for name, have in iteritems(haved):
                if name in wantd:
                    merged = deepcopy(have)
                    merged.update(wantd[name])
                    wantd[name] = merged
        if self.state == "deleted":
            haved = {name: entry for name, entry in iteritems(haved) if not wantd or name in wantd}
            wantd = {}
        if self.state in ["overridden", "deleted"]:
            for name, have in iteritems(haved):
                if name not in wantd:
                    self.compare(parsers=self.parsers, want={}, have=have)
        for name, want in iteritems(wantd):
            self.compare(parsers=self.parsers, want=want, have=haved.get(name, {}))
