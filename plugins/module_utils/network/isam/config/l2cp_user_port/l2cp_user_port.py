from __future__ import absolute_import, division, print_function

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import ResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.l2cp_user_port.l2cp_user_port import L2cpUserPortFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.l2cp import L2cpUserPortTemplate


class L2cpUserPort(ResourceModule):
    def __init__(self, module):
        self.template = L2cpUserPortTemplate()
        super(L2cpUserPort, self).__init__(empty_fact_val=[], facts_module=L2cpUserPortFacts(module), module=module, resource="l2cp_user_port", tmplt=self)

    def get_parser(self, name):
        return {"compval": name}

    def execute_module(self):
        if self.state == "parsed":
            return {"parsed": self.template.parse(self._module.params.get("running_config")), "changed": False}
        if self.state == "rendered":
            return {"rendered": self.template.render(self._module.params.get("config")), "changed": False}
        desired = self.want or []
        current = {item["name"]: item for item in self.have or []}
        if self.state == "deleted":
            targets = desired or list(current.values())
            self.commands = self.template.render(
                [dict(item, partition_id=None) for item in targets]
            )
        else:
            self.commands = []
            if self.state == "overridden":
                wanted_names = {item["name"] for item in desired}
                self.commands.extend(
                    self.template.render([dict(item, partition_id=None)])
                    for name, item in current.items()
                    if name not in wanted_names
                )
            if self.state in ("replaced", "overridden"):
                self.commands.extend(
                    self.template.render([dict(current[item["name"]], partition_id=None)])
                    for item in desired
                    if item["name"] in current
                )
            if self.state == "merged":
                desired = [dict(current.get(item["name"], {}), **item) for item in desired]
            self.commands.extend(self.template.render(desired))
            self.commands = [command for commands in self.commands for command in (
                commands if isinstance(commands, list) else [commands]
            )]
        if self.commands:
            self.run_commands()
        return self.result
