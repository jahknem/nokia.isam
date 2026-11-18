# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
)
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
        """The whole resource, or only the instances named in config (targeted gathering)."""
        return get_targeted_config(self._module, connection, "alarm", "info configure alarm flat", {
            "entries": "info configure alarm entry %s flat",
            "filters": self._filter_commands,
            "custom_profiles": "info configure alarm custom-profile %s flat",
            "hgutr069_custs": "info configure alarm hgutr069-cust %s flat",
        }, bare_sections=("custom_profiles",))

    @staticmethod
    def _filter_commands(identity):
        """A filter with its suppressions (the parser files them under the temporal filter)."""
        fltr_type, filterid = identity
        commands = ["info configure alarm filter %s filterid %s flat" % (fltr_type, filterid)]
        if fltr_type == "temporal":
            commands.append("info configure alarm suppression filterid %s flat" % filterid)
        return commands

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)

        alarm_parser = AlarmTemplate(lines=data.splitlines(), module=self._module)
        parsed = alarm_parser.parse()

        if "entries" in parsed:
            parsed["entries"] = list(parsed["entries"].values())
        for key in ("filters", "custom_profiles", "hgutr069_custs"):
            if key in parsed:
                parsed[key] = list(parsed[key].values())
        for fltr in parsed.get("filters", []):
            if isinstance(fltr.get("suppressions"), dict):
                fltr["suppressions"] = list(fltr["suppressions"].values())

        ansible_facts["ansible_network_resources"].pop("alarm", None)

        params = utils.remove_empties(
            alarm_parser.validate_config(self.argument_spec, {"config": parsed}, redact=True)
        ) or {}

        facts["alarm"] = params.get("config") or {}
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts
