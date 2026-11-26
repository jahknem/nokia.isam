from __future__ import absolute_import, division, print_function

from ansible.module_utils.common.text.converters import to_text
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts import get_resource_connection
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.efm_oam import EfmOamTemplate


class EfmOamFacts(object):
    def __init__(self, module):
        self._module = module
        self.template = EfmOamTemplate()

    def get_config(self, connection):
        """The whole resource, or only the interfaces named in config (targeted gathering)."""
        return get_targeted_config(self._module, connection, "efm_oam_interface", "info configure efm-oam interface flat", {
            "config": "info configure efm-oam interface %s flat",
        }, write_states=True)

    def get_facts(self, resource_facts_type=None, data=None, **kwargs):
        resource = (resource_facts_type or ["efm_oam_interface"])[0]
        if data is None:
            # The resource module reads the device here (it used to parse nothing).
            try:
                data = self.get_config(get_resource_connection(self._module))
            except Exception as exc:  # like netcommon's facts: a clear failure, no traceback
                self._module.fail_json(msg=to_text(exc))
        return {"ansible_network_resources": {resource: self.template.parse(data)}}, []

    def populate_facts(self, connection, ansible_facts, data=None):
        if data is None:
            data = self.get_config(connection)
        ansible_facts["ansible_network_resources"]["efm_oam_interface"] = self.template.parse(data)
        return ansible_facts
