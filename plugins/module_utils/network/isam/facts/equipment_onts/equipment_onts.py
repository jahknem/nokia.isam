# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    unwrap_response,
    validate_config_safe,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.equipment_onts.equipment_onts import (
    Equipment_ontsArgs,
)


class Equipment_ontsFacts(object):
    """The isam equipment_onts facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Equipment_ontsArgs.argument_spec

    def get_config(self, connection):
        return connection.get("info configure equipment ont")

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)
        data = unwrap_response(data)

        objs = self._parse_config(data)
        ansible_facts["ansible_network_resources"].pop("equipment_onts", None)
        params = utils.remove_empties(
            validate_config_safe(self.argument_spec, {"config": objs})
        )
        facts["equipment_onts"] = params.get("config", {})
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts

    def _parse_config(self, config):
        result = {"interfaces": [], "slots": [], "sw_ctrls": []}
        current = None
        current_type = None

        if not config:
            return result

        lines = [line.strip() for line in str(config).splitlines() if line.strip()]
        if any(line.startswith("configure equipment ont ") for line in lines):
            config = "\n".join(
                line.replace("configure equipment ont ", "", 1)
                for line in lines
                if line.startswith("configure equipment ont ")
            )

        for raw_line in config.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith("echo"):
                continue
            if line in ("configure equipment", "ont"):
                continue
            if line == "exit":
                if current is not None:
                    result[current_type].append(current)
                    current = None
                    current_type = None
                continue

            parts = line.split()
            if parts[0] == "interface" and len(parts) >= 2:
                if current is not None:
                    result[current_type].append(current)
                current_type = "interfaces"
                current = {"ont_idx": parts[1]}
                self._set_pairs(current, parts[2:])
            elif parts[0] == "slot" and len(parts) >= 2:
                if current is not None:
                    result[current_type].append(current)
                current_type = "slots"
                current = {"ont_slot_idx": parts[1]}
                self._set_pairs(current, parts[2:])
            elif parts[0] == "sw-ctrl" and len(parts) >= 2:
                if current is not None:
                    result[current_type].append(current)
                current_type = "sw_ctrls"
                current = {"sw_ctrl_id": int(parts[1])}
                self._set_pairs(current, parts[2:])
            elif current is not None:
                self._set_pairs(current, parts)

        if current is not None:
            result[current_type].append(current)

        return result

    def _set_pairs(self, item, parts):
        idx = 0
        while idx < len(parts):
            key = parts[idx].replace("-", "_")
            if idx + 1 >= len(parts):
                item[key] = True
                idx += 1
                continue
            value = parts[idx + 1]
            if key in ("plndnumdataports", "plndnumvoiceports"):
                value = int(value)
            item[key] = value
            idx += 2
