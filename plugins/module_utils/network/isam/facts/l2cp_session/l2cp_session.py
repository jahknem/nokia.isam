from __future__ import absolute_import, division, print_function

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.l2cp import L2cpSessionTemplate


class L2cpSessionFacts(object):
    def __init__(self, module):
        self._module = module
        self.template = L2cpSessionTemplate()

    def get_facts(self, resource_facts_type=None, data=None, **kwargs):
        resource = (resource_facts_type or ["l2cp_session"])[0]
        return {"ansible_network_resources": {resource: self.template.parse(data)}}, []

    def populate_facts(self, connection, ansible_facts, data=None):
        data = data if data is not None else connection.get("info configure l2cp session flat")
        ansible_facts["ansible_network_resources"]["l2cp_session"] = self.template.parse(data)
        return ansible_facts
