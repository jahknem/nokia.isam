# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.isam_equipment.isam_equipment import (
    Isam_equipmentArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.isam_equipment import (
    Isam_equipmentTemplate,
)


class Isam_equipmentFacts(object):
    """The isam equipment facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Isam_equipmentArgs.argument_spec

    def get_config(self, connection):
        return connection.get("info configure equipment flat")

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)
        data = unwrap_response(data)

        data = self._flatten_config(data)
        parser = Isam_equipmentTemplate(lines=data, module=self._module)
        parsed = parser.parse()

        objs = {
            "shelves": list(parsed.get("shelves", {}).values()),
            "slots": list(parsed.get("slots", {}).values()),
            "appliques": list(parsed.get("appliques", {}).values()),
            "protection_groups": list(parsed.get("protection_groups", {}).values()),
        }

        for group in objs["protection_groups"]:
            group["id"] = int(group["id"])
            if "eps_quenchfactor" in group:
                group["eps_quenchfactor"] = int(group["eps_quenchfactor"])

        ansible_facts["ansible_network_resources"].pop("isam_equipment", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )
        facts["isam_equipment"] = params.get("config", {})
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    def _flatten_config(self, config):
        flat_config = []
        if not config:
            return flat_config

        current = None
        in_equipment = False
        resources = ("shelf ", "slot ", "applique ", "protection-group ")
        fields = ("planned-type ", "unlock", "no unlock", "admin-status ", "eps-quenchfactor ")

        for raw_line in config.splitlines():
            line = raw_line.split("#", 1)[0].rstrip()
            stripped = line.strip()
            if not stripped or stripped.startswith("echo") or stripped.startswith("#"):
                continue

            if line.startswith((
                "configure equipment shelf ",
                "configure equipment slot ",
                "configure equipment applique ",
                "configure equipment protection-group ",
            )):
                flat_config.append(line)
                continue

            if stripped == "equipment":
                in_equipment = True
                current = None
                continue
            if stripped == "exit":
                current = None
                continue
            if not in_equipment:
                continue

            if line == stripped and stripped.startswith(resources):
                current = "configure equipment " + stripped
                continue
            if current and stripped.startswith(fields):
                flat_config.append(current + " " + stripped)

        return flat_config
