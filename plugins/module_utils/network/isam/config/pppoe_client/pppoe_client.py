# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import ResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.pppoe_client import PppoeClientTemplate


class PppoeClient(ResourceModule):
    def __init__(self, module, kind):
        self.template = PppoeClientTemplate(kind)
        self.kind = kind
        super(PppoeClient, self).__init__(
            empty_fact_val=[], facts_module=_LocalFacts(self.template), module=module,
            resource="pppoe_client_%s" % kind, tmplt=_TemplateAdapter(self.template),
        )

    def execute_module(self):
        config = self._module.params.get("config") or []
        if self.state == "parsed":
            return self.result
        elif self.state == "rendered":
            self.commands = self.template.render(config)
        else:
            current = {item["name"]: item for item in self.have or []}
            desired = {item["name"]: item for item in config}
            self.commands = []
            if self.state == "deleted":
                targets = desired or current
                self.commands = [self._delete_command(name) for name in targets]
            else:
                if self.state == "overridden":
                    self.commands.extend(
                        self._delete_command(name)
                        for name in current
                        if name not in desired
                    )
                if self.state in ("replaced", "overridden"):
                    self.commands.extend(
                        self._delete_command(name)
                        for name in desired
                        if name in current
                    )
                if self.state == "merged":
                    merged = [dict(current.get(item["name"], {}), **item) for item in config]
                    config = [item for item in merged if item != current.get(item["name"])]
                elif self.state in ("replaced", "overridden"):
                    config = [item for item in config if item != current.get(item["name"])]
                self.commands.extend(self.template.render(config))
            if self.commands:
                self.run_commands()
        return self.result

    def _delete_command(self, name):
        return "configure pppoe-client no %s %s" % (self.kind, name)


class _LocalFacts(object):
    def __init__(self, template):
        self.template = template

    def get_facts(self, resource_facts_type=None, data=None, **kwargs):
        resource = resource_facts_type[0]
        return {"ansible_network_resources": {resource: self.template.parse(data)}} , []


class _TemplateAdapter(object):
    def __init__(self, template):
        self.template = template

    def get_parser(self, name):
        return {"compval": name}
