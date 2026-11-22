# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from ansible.module_utils.common.text.converters import to_text
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts import get_resource_connection
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    assert_targeted_request,
    finish_targeted_outcomes,
    get_scoped_config,
    requested_identities,
    selector_key,
    targeted_explicit,
    targeted_outcomes,
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.arp_relay import Isam_arp_relayTemplate


class Isam_arp_relayFacts(object):
    """Facts adapter for the resource-local ARP relay implementation."""

    def __init__(self, module):
        self._module = module
        self.argument_spec = {}

    def get_config(self, connection):
        """The whole resource, or only the ports named in config (targeted gathering)."""
        assert_targeted_request(self._module, "isam_arp_relay", ("config",))
        collector = targeted_outcomes(self._module, "isam_arp_relay")
        commands = []
        selectors = {}
        for port in requested_identities(self._module, "isam_arp_relay"):
            command = "info configure arp-relay statistics %s flat" % port
            commands.append(command)
            selectors[command] = ("config", selector_key(port))
        data = get_scoped_config(
            self._module,
            connection,
            None,
            "info configure arp-relay flat",
            commands,
            outcomes=collector,
            selectors=selectors,
            # An explicit gathered request that names instances must not silently widen
            # to the whole-family read when none of them became a read command.
            require_targeted=targeted_explicit(self._module, "config"),
        )
        finish_targeted_outcomes(self._module, collector)
        return data

    def populate_facts(self, connection, ansible_facts, data=None):
        if data is None:
            data = self.get_config(connection)
        parsed = Isam_arp_relayTemplate(
            lines=unwrap_response(data).splitlines(), module=self._module
        ).parse()
        ansible_facts["ansible_network_resources"]["isam_arp_relay"] = list(parsed.values())
        return ansible_facts

    def get_facts(self, legacy_facts_type=None, resource_facts_type=None, data=None):
        connection = get_resource_connection(self._module)
        facts = {"ansible_network_resources": {}}
        try:
            self.populate_facts(connection, facts, data)
        except Exception as exc:  # like netcommon's facts: a clear failure, no traceback
            self._module.fail_json(msg=to_text(exc))
        return facts, []
