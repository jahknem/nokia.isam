# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from ansible.module_utils.common.text.converters import to_text
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import ResourceModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base import get_resource_connection
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import get_targeted_config
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.pppoe_client import Pppoel2StatisticsTemplate


class Pppoel2(ResourceModule):
    def __init__(self, module):
        self.template = Pppoel2StatisticsTemplate()
        super(Pppoel2, self).__init__(
            empty_fact_val=[], facts_module=_LocalFacts(self.template, module), module=module,
            resource="pppoel2_statistics", tmplt=_TemplateAdapter(),
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
                self.commands = self.template.render(
                    [{"name": name, "enabled": False} for name in targets]
                )
            else:
                if self.state == "overridden":
                    self.commands.extend(
                        self.template.render([{"name": name, "enabled": False}])
                        for name in current
                        if name not in desired
                    )
                if self.state in ("replaced", "overridden"):
                    self.commands.extend(
                        self.template.render([{"name": name, "enabled": False}])
                        for name in desired
                        if name in current
                    )
                if self.state == "merged":
                    config = [dict(current.get(item["name"], {}), **item) for item in config]
                self.commands.extend(self.template.render(config))
                self.commands = [
                    command
                    for commands in self.commands
                    for command in (commands if isinstance(commands, list) else [commands])
                ]
            self.run_commands()
        return self.result


class _LocalFacts(object):
    def __init__(self, template, module=None):
        self.template = template
        self._module = module

    def get_config(self, connection):
        """All statistics settings, or only those named in config with state gathered (targeted gathering)."""
        return get_targeted_config(self._module, connection, "pppoel2_statistics", "info configure pppoel2 statistics flat",
                                   {"config": "info configure pppoel2 statistics %s flat"})

    def get_facts(self, resource_facts_type=None, data=None, **kwargs):
        resource = resource_facts_type[0]
        state = (getattr(self._module, "params", None) or {}).get("state")
        if data is None and state == "gathered":
            # gathered reads the device here; the other states keep their former behaviour.
            try:
                data = self.get_config(get_resource_connection(self._module))
            except Exception as exc:  # like netcommon's facts: a clear failure, no traceback
                self._module.fail_json(msg=to_text(exc))
        return {"ansible_network_resources": {resource: self.template.parse(data)}} , []


class _TemplateAdapter(object):
    def get_parser(self, name):
        return {"compval": name}
