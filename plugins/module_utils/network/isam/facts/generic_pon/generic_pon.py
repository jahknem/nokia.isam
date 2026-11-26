# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.generic_pon.generic_pon import (
    Generic_ponArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.generic_pon import TABLE


class Generic_ponFacts(object):
    """The isam generic_pon facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Generic_ponArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        if data is None:
            data = connection.get("info configure generic-pon flat")
        params = TABLE.without_defaults(TABLE.parse(unwrap_response(data)))
        ansible_facts["ansible_network_resources"].pop("generic_pon", None)
        ansible_facts["ansible_network_resources"]["generic_pon"] = params
        return ansible_facts
