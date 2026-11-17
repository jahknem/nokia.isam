# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.linetest import LinetestTemplate


class LinetestFacts(object):
    """Gather LineTest configuration without invoking any test command."""

    def __init__(self, module):
        self._module = module
        self.template = LinetestTemplate()

    def get_config(self, connection):
        """The whole resource, or only the sessions/parameters named in config (targeted gathering).

        Same hierarchical (not flat) output as the whole-resource read.
        """
        return unwrap_response(get_targeted_config(self._module, connection, "linetest", "info configure linetest", {
            "sessions": "info configure linetest single ltsession %s",
            "parameters": "info configure linetest single ltparm %s %s",
        }))

    def populate_facts(self, connection, ansible_facts, data=None):
        parsed = self.template.parse(data if data is not None else self.get_config(connection))
        ansible_facts.setdefault("ansible_network_resources", {})["linetest"] = parsed
        return ansible_facts
