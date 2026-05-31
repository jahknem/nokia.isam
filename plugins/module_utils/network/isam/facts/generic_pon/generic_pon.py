# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.generic_pon.generic_pon import (
    Generic_ponArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.generic_pon import (
    Generic_ponTemplate,
)


class Generic_ponFacts(object):
    """The isam generic_pon facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Generic_ponArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = connection.get("info configure generic-pon")

        parser = Generic_ponTemplate(lines=data.splitlines())
        parsed = parser.parse()

        ansible_facts["ansible_network_resources"].pop("generic_pon", None)
        facts["generic_pon"] = utils.remove_empties(parsed) or {}
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts
