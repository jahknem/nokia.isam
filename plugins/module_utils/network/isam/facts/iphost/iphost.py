# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import unwrap_response

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.iphost.iphost import (
    IphostArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.iphost import (
    IphostTemplate,
)


class IphostFacts(object):
    """The isam iphost facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = IphostArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = connection.get("info configure iphost flat")

        if isinstance(data, tuple):
            data = data[0]

        data = unwrap_response(data)

        parser = IphostTemplate(lines=[line.strip() for line in str(data or "").splitlines() if line.strip()])
        parsed = parser.parse()

        ansible_facts["ansible_network_resources"].pop("iphost", None)
        facts["iphost"] = utils.remove_empties(parsed) or {}
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts
