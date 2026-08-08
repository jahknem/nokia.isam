# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from anytree import Node
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.pon_interfaces.pon_interfaces import Pon_interfacesArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.pon_interfaces import Pon_interfacesTemplate


class Pon_interfacesFacts(object):
    """The isam pon_interfaces facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Pon_interfacesArgs.argument_spec

    def get_config(self, connection):
        return connection.get("info configure pon interface flat")

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}
        if not data:
            data = self.get_config(connection)
        data = unwrap_response(data)
        data = self._flatten_config(data)

        pon_interfaces_parser = Pon_interfacesTemplate(lines=data, module=self._module)
        objs = list(pon_interfaces_parser.parse().values())

        ansible_facts["ansible_network_resources"].pop("pon_interfaces", None)
        params = utils.remove_empties(
            pon_interfaces_parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )
        facts["pon_interfaces"] = params.get("config", [])
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    def _count_spaces(self, line):
        spaces = 0
        for char in line:
            if char == " ":
                spaces += 1
            else:
                break
        return spaces

    def _parse_config_to_tree(self, config):
        if not config:
            return None
        last_spaces = 0
        root = None
        parent_node = None
        prev_node = None
        for line in config.splitlines():
            if line.startswith("echo") or line.startswith("#"):
                continue

            if parent_node is None:
                root = Node(line.split("#", 1)[0].strip())
                parent_node = root
                prev_node = root
            elif "exit" in line:
                if self._count_spaces(line) < last_spaces:
                    parent_node = parent_node.parent
                else:
                    continue
            elif self._count_spaces(line) > last_spaces:
                parent_node = prev_node
                prev_node = Node(line.split("#", 1)[0].strip(), parent=prev_node)
            else:
                prev_node = Node(line.split("#", 1)[0].strip(), parent=parent_node)

            last_spaces = self._count_spaces(line)
        return root

    def _flatten_config(self, config):
        if not config:
            return None
        lines = [line.strip() for line in str(config).splitlines() if line.strip()]
        if any(line.startswith("configure pon interface ") for line in lines):
            return [line for line in lines if line.startswith("configure pon interface ")]
        root = self._parse_config_to_tree(config)
        if root is None:
            return None
        flat_config = []
        for leave in root.leaves:
            line = []
            for node in leave.path:
                line.append(node.name)
            flat_config.append(" ".join(line))
        return flat_config
