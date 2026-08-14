from __future__ import absolute_import, division, print_function

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import ResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.l2cp.l2cp import L2cpFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.l2cp import L2cpTemplate


class L2cp(ResourceModule):
    def __init__(self, module):
        self.template = L2cpTemplate()
        super(L2cp, self).__init__(empty_fact_val=[], facts_module=L2cpFacts(module), module=module, resource="l2cp", tmplt=self)

    def get_parser(self, name):
        return {"compval": name}

    def execute_module(self):
        if self.state == "parsed":
            return {"parsed": self.template.parse(self._module.params.get("running_config")), "changed": False}
        if self.state == "rendered":
            return {"rendered": self.template.render(self._module.params.get("config")), "changed": False}
        desired = self.want or []
        current = self.have or []
        if self.state == "deleted" and any(
            item.get("partition_type") != "no-partition" for item in current
        ) and self.before:
            self.commands = self.template.render([{"partition_type": "no-partition"}])
        elif self.state == "deleted":
            self.commands = []
        elif self.state == "overridden" and not desired and current:
            self.commands = self.template.render([{"partition_type": "no-partition"}])
        elif self.state == "merged" and current and desired:
            merged = dict(current[0])
            merged.update(desired[0])
            self.commands = [] if merged == current[0] else self.template.render([merged])
        elif self.state in ("replaced", "overridden") and desired == current:
            self.commands = []
        else:
            self.commands = self.template.render(desired)
        if self.commands:
            self.run_commands()
        return self.result
