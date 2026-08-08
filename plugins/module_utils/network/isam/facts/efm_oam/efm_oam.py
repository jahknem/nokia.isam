from __future__ import absolute_import, division, print_function

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.efm_oam import EfmOamTemplate


class EfmOamFacts(object):
    def __init__(self, module):
        self._module = module
        self.template = EfmOamTemplate()

    def get_facts(self, resource_facts_type=None, data=None, **kwargs):
        resource = (resource_facts_type or ["efm_oam_interface"])[0]
        return {"ansible_network_resources": {resource: self.template.parse(data)}}, []

    def populate_facts(self, connection, ansible_facts, data=None):
        if data is None:
            data = connection.get("info configure efm-oam interface flat")
        ansible_facts["ansible_network_resources"]["efm_oam_interface"] = self.template.parse(data)
        return ansible_facts
