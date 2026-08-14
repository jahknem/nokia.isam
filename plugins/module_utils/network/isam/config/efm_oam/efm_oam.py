from __future__ import absolute_import, division, print_function

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import ResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.efm_oam.efm_oam import EfmOamFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.efm_oam import EfmOamTemplate


class EfmOam(ResourceModule):
    def __init__(self, module):
        self.template = EfmOamTemplate()
        super(EfmOam, self).__init__(
            empty_fact_val=[], facts_module=EfmOamFacts(module), module=module,
            resource="efm_oam_interface", tmplt=self,
        )

    def get_parser(self, name):
        return {"compval": name}

    def execute_module(self):
        if self.state == "parsed":
            return {"parsed": self.template.parse(self._module.params.get("running_config")), "changed": False}
        elif self.state == "rendered":
            return {"rendered": self.template.render(self._module.params.get("config")), "changed": False}
        else:
            config = self._module.params.get("config") or []
            if self.state == "deleted":
                requested = {item["name"] for item in config}
                current = self.have or []
                targets = [
                    item for item in current
                    if not requested or item.get("name") in requested
                ]
                self.commands = self.template.render([
                    {
                        "name": item["name"],
                        "admin_up": False,
                        "passive_mode": False,
                        "keep_alive_intvl": None,
                        "response_intvl": None,
                    }
                    for item in targets
                ])
            else:
                self.commands = self.template.render(config)
            if self.commands:
                self.run_commands()
        return self.result
