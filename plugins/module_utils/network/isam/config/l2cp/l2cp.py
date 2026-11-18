from __future__ import absolute_import, division, print_function

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.l2cp.l2cp import L2cpFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.l2cp import L2cpTemplate


class L2cp(IsamResourceModule):
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
        if self.state == "gathered":
            return self.result
        # A single settings block with one attribute: "info configure l2cp flat" omits the default
        # (no-partition), so an empty read means no-partition.
        current = (self.have or [{}])[-1].get("partition_type") or "no-partition"
        if self.state == "deleted":
            target = "no-partition"
        else:
            # merged/replaced/overridden: the one attribute is always set (argspec default no-partition).
            target = ((self.want or [{}])[-1].get("partition_type")) or "no-partition"
        self.commands = [] if target == current else self.template.render([{"partition_type": target}])
        if self.commands:
            self.run_commands()
        return self.result
