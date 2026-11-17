from ansible.module_utils.common.text.converters import to_text
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts import get_resource_connection
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.cfm import CfmTemplate


class CfmFacts(object):
    def __init__(self, module):
        self._module = module
        self.argument_spec = {}

    def get_config(self, connection):
        """The whole resource, or only the domains and Y.1731 PM sessions named in config (targeted gathering)."""
        return get_targeted_config(self._module, connection, "isam_cfm", "info configure cfm flat", {
            "domains": "info configure cfm domain %s flat",
            "y1731pm": "info configure cfm y1731pm domain %s association %s mep %s session-id %s flat",
        })

    def populate_facts(self, connection, ansible_facts, data=None):
        if data is None:
            data = self.get_config(connection)
        ansible_facts["ansible_network_resources"]["isam_cfm"] = CfmTemplate(lines=unwrap_response(data).splitlines(), module=self._module).parse()
        return ansible_facts

    def get_facts(self, legacy_facts_type=None, resource_facts_type=None, data=None):
        facts = {"ansible_network_resources": {}}
        connection = get_resource_connection(self._module)
        if data is None:
            try:
                data = self.get_config(connection)
            except Exception as exc:  # like netcommon's facts: a clear failure, no traceback
                self._module.fail_json(msg=to_text(exc))
        self.populate_facts(connection, facts, data)
        return facts, []
