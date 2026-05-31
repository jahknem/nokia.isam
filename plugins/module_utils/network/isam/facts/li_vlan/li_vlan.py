# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.li_vlan.li_vlan import (
    Li_vlanArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.li_vlan import (
    Li_vlanTemplate,
)


class Li_vlanFacts(object):
    """The isam li_vlan facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Li_vlanArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = connection.get("info configure li_vlan")

        parser = Li_vlanTemplate(lines=data.splitlines())
        parsed = parser.parse()

        ansible_facts["ansible_network_resources"].pop("li_vlan", None)
        facts["li_vlan"] = utils.remove_empties(parsed) or {}
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts
