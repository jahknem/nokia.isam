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
            pass
        elif self.state == "rendered":
            self.commands = self.template.render(config)
        else:
            self.commands = self.template.render(config)
            self.run_commands()
        return self.result


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
