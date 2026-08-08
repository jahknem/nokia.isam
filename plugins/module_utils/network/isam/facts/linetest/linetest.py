# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import unwrap_response
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.linetest import LinetestTemplate


class LinetestFacts(object):
    """Gather LineTest configuration without invoking any test command."""

    def __init__(self, module):
        self._module = module
        self.template = LinetestTemplate()

    def get_config(self, connection):
        return unwrap_response(connection.get("info configure linetest"))

    def populate_facts(self, connection, ansible_facts, data=None):
        parsed = self.template.parse(data if data is not None else self.get_config(connection))
        ansible_facts.setdefault("ansible_network_resources", {})["linetest"] = parsed
        return ansible_facts
