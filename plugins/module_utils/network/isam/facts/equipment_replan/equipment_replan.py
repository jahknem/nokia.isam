# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    unwrap_response,
    validate_config_safe,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.equipment_replan.equipment_replan import (
    Equipment_replanArgs,
)


class Equipment_replanFacts(object):
    """The isam equipment_replan facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Equipment_replanArgs.argument_spec

    def get_config(self, connection):
        return connection.get("info configure equipment replan")

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)
        data = unwrap_response(data)

        objs = self._parse_config(data)
        ansible_facts["ansible_network_resources"].pop("equipment_replan", None)
        params = utils.remove_empties(
            validate_config_safe(self.argument_spec, {"config": objs})
        )
        facts["equipment_replan"] = params.get("config", {})
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts

    def _parse_config(self, config):
        result = {}

        if not config:
            return result

        for raw_line in config.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith("echo"):
                continue
            parts = line.split()
            if parts[0] == "boardautoreplan" and len(parts) >= 2:
                result["board_auto_replan"] = parts[1]

        return result
