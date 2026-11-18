from __future__ import absolute_import, division, print_function

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.l2cp_user_port.l2cp_user_port import L2cpUserPortFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.l2cp import L2cpUserPortTemplate


class L2cpUserPort(IsamResourceModule):
    """User-port partition assignments.

    The CLI identity is (user-port, partition-id): the removal form is
    "configure l2cp no user-port <port> partition-id <id>" and needs the assigned id,
    which is taken from the device.
    """

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
        if self.state == "gathered":
            return self.result
        desired = self.want or []
        wanted_names = set(item["name"] for item in desired)
        current = {}
        for item in self.have or []:
            if item.get("partition_id") is not None:
                current.setdefault(item["name"], []).append(str(item["partition_id"]))
        self.commands = []
        if self.state == "deleted":
            for name, partitions in current.items():
                if not wanted_names or name in wanted_names:
                    self.commands.extend(self._remove(name, partitions))
        else:
            if self.state == "overridden":
                for name, partitions in current.items():
                    if name not in wanted_names:
                        self.commands.extend(self._remove(name, partitions))
            for item in desired:
                partitions = current.get(item["name"], [])
                wanted = item.get("partition_id")
                wanted = None if wanted is None else str(wanted)
                if self.state in ("replaced", "overridden"):
                    self.commands.extend(self._remove(item["name"], [pid for pid in partitions if pid != wanted]))
                if wanted is not None and wanted not in partitions:
                    self.commands.append("configure l2cp user-port %s partition-id %s" % (item["name"], wanted))
        if self.commands:
            self.run_commands()
        return self.result

    @staticmethod
    def _remove(name, partitions):
        return ["configure l2cp no user-port %s partition-id %s" % (name, pid) for pid in partitions]
