from __future__ import absolute_import, division, print_function

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.l2cp.l2cp import L2cpFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.l2cp import L2cpTemplate


class L2cp(IsamResourceModule):
    def __init__(self, module):
        self.template = L2cpTemplate()
        super(L2cp, self).__init__(empty_fact_val=[], facts_module=L2cpFacts(module), module=module, resource="l2cp", tmplt=self.template)

    def generate_commands(self):
        if self.state == "rendered":
            # an entry without partition_type renders nothing (never the reset)
            self.commands = self.template.render([item for item in self.want or [] if item.get("partition_type")])
            return
        # A single settings block with one attribute: "info configure l2cp flat" omits the default
        # (no-partition), so an empty read means no-partition.
        current = (self.have or [{}])[-1].get("partition_type") or "no-partition"
        wanted = (self.want or [{}])[-1].get("partition_type")
        if self.state == "deleted":
            target = "no-partition"
        elif self.state == "merged":
            target = wanted or current  # merged leaves an unnamed setting alone
        else:
            target = wanted or "no-partition"  # replaced/overridden: unnamed means the default
        self.commands = [] if target == current else self.template.render([{"partition_type": target}])
