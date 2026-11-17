# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import re

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
        if self.state in ("parsed", "gathered"):
            # no commands: the result is the parsed / gathered facts
            return self.result
        elif self.state == "rendered":
            self.commands = self.template.render(config)
        else:
            # The only attribute is whether statistics are enabled on a vlan-port
            # ("configure pppoel2 [no] statistics <vlan-port>"): enabled ports are the configured instances.
            # Names compare as "vlan-port:<port>" ("vlan-port <port>" is the same port).
            enabled = dict((_port(item["name"]), item["name"]) for item in self.have or [] if item.get("enabled", True))
            desired = dict((_port(item["name"]), (item["name"], item.get("enabled", True) is not False)) for item in config)
            if self.state == "deleted":
                targets = [name for port, name in enabled.items() if not desired or port in desired]
            else:
                targets = [name for port, name in enabled.items() if self.state == "overridden" and port not in desired]
                targets.extend(enabled[port] for port, (name, on) in desired.items() if not on and port in enabled)
            self.commands = self.template.render([{"name": name, "enabled": False} for name in targets])
            if self.state != "deleted":
                self.commands.extend(self.template.render(
                    [{"name": name, "enabled": True} for port, (name, on) in desired.items() if on and port not in enabled]
                ))
            if self.commands:
                self.run_commands()
        return self.result


def _port(name):
    return re.sub(r"^vlan-port\s+", "vlan-port:", str(name).strip())


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
        if data is None:
            # Every state reads the device: gathered (targeted when config names instances) and the
            # write states (the whole resource, so merged/replaced/overridden/deleted compare against it).
            try:
                data = self.get_config(get_resource_connection(self._module))
            except Exception as exc:  # like netcommon's facts: a clear failure, no traceback
                self._module.fail_json(msg=to_text(exc))
        return {"ansible_network_resources": {resource: self.template.parse(data)}}, []


class _TemplateAdapter(object):
    def get_parser(self, name):
        return {"compval": name}
