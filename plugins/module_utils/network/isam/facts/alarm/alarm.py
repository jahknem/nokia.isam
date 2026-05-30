# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.alarm import (
    AlarmTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.alarm.alarm import (
    AlarmArgs,
)


class AlarmFacts(object):
    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = AlarmArgs.argument_spec

    def get_config(self, connection):
        return connection.get("info configure alarm flat")

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)

        alarm_parser = AlarmTemplate(lines=data.splitlines(), module=self._module)
        parsed = alarm_parser.parse()

        if "entries" in parsed:
            parsed["entries"] = list(parsed["entries"].values())
        if "filters" in parsed:
            parsed["filters"] = list(parsed["filters"].values())

        ansible_facts["ansible_network_resources"].pop("alarm", None)

        params = utils.remove_empties(
            alarm_parser.validate_config(self.argument_spec, {"config": parsed}, redact=True)
        ) or {}

        facts["alarm"] = params.get("config") or {}
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts
