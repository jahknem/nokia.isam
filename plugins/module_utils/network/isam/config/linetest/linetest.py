# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.linetest import LinetestTemplate


class Linetest(object):
    """Resource implementation restricted to rendering and read-only states."""

    def __init__(self, module):
        self.module = module
        self.template = LinetestTemplate()

    def execute_module(self):
        state = self.module.params["state"]
        result = {"changed": False}
        if state == "rendered":
            result["rendered"] = self.template.render(self.module.params.get("config") or {})
        elif state == "parsed":
            result["parsed"] = self.template.parse(self.module.params.get("running_config"))
        else:
            from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.linetest.linetest import LinetestFacts
            from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base import get_resource_connection
            facts = LinetestFacts(self.module).populate_facts(
                get_resource_connection(self.module), {"ansible_network_resources": {}}
            )
            result["gathered"] = facts["ansible_network_resources"]["linetest"]
        return result
