from __future__ import absolute_import, division, print_function

from ansible.module_utils.common.text.converters import to_text
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts import get_resource_connection
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import get_targeted_config
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.l2cp import L2cpTemplate


class L2cpFacts(object):
    def __init__(self, module):
        self._module = module
        self.template = L2cpTemplate()

    def get_config(self, connection):
        """The global L2CP settings (a single block: always read completely)."""
        return get_targeted_config(self._module, connection, "l2cp", "info configure l2cp flat", {})

    def get_facts(self, resource_facts_type=None, data=None, **kwargs):
        resource = (resource_facts_type or ["l2cp"])[0]
        if data is None:
            # Every state reads the device: gathered (targeted when config names instances) and the
            # write states (the whole resource, so merged/replaced/overridden/deleted compare against it).
            try:
                data = self.get_config(get_resource_connection(self._module))
            except Exception as exc:  # like netcommon's facts: a clear failure, no traceback
                self._module.fail_json(msg=to_text(exc))
        return {"ansible_network_resources": {resource: self.template.parse(data)}}, []

    def populate_facts(self, connection, ansible_facts, data=None):
        data = data if data is not None else self.get_config(connection)
        ansible_facts["ansible_network_resources"]["l2cp"] = self.template.parse(data)
        return ansible_facts
