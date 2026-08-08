# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts import get_resource_connection
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import unwrap_response
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.arp_relay import Isam_arp_relayTemplate


class Isam_arp_relayFacts(object):
    """Facts adapter for the resource-local ARP relay implementation."""

    def __init__(self, module):
        self._module = module
        self.argument_spec = {}

    def populate_facts(self, connection, ansible_facts, data=None):
        if data is None:
            data = connection.get("info configure arp-relay flat")
        parsed = Isam_arp_relayTemplate(
            lines=unwrap_response(data).splitlines(), module=self._module
        ).parse()
        ansible_facts["ansible_network_resources"]["isam_arp_relay"] = list(parsed.values())
        return ansible_facts

    def get_facts(self, legacy_facts_type=None, resource_facts_type=None, data=None):
        connection = get_resource_connection(self._module)
        facts = {"ansible_network_resources": {}}
        self.populate_facts(connection, facts, data)
        return facts, []
