from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts import get_resource_connection
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import unwrap_response
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.cfm import CfmTemplate


class CfmFacts(object):
    def __init__(self, module):
        self._module = module
        self.argument_spec = {}

    def populate_facts(self, connection, ansible_facts, data=None):
        if data is None:
            data = connection.get("info configure cfm flat")
        ansible_facts["ansible_network_resources"]["isam_cfm"] = CfmTemplate(lines=unwrap_response(data).splitlines(), module=self._module).parse()
        return ansible_facts

    def get_facts(self, legacy_facts_type=None, resource_facts_type=None, data=None):
        facts = {"ansible_network_resources": {}}
        self.populate_facts(get_resource_connection(self._module), facts, data)
        return facts, []
