# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.ani_onts.ani_onts import (
    Ani_ontsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ani_onts import (
    Ani_ontsTemplate,
)


class Ani_ontsFacts(object):
    """The isam ani_onts facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Ani_ontsArgs.argument_spec

    def get_config(self, connection):
        return connection.get("info configure ani ont")

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}
        if not data:
            data = self.get_config(connection)
        if isinstance(data, tuple):
            data = data[0]

        data = self._flatten_config(data)
        ani_onts_parser = Ani_ontsTemplate(lines=data, module=self._module)
        objs = list(ani_onts_parser.parse().values())

        ansible_facts["ansible_network_resources"].pop("ani_onts", None)
        params = utils.remove_empties(
            ani_onts_parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        ) or {}
        facts["ani_onts"] = list(params.get("config") or [])
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    @staticmethod
    def _count_spaces(line):
        return len(line) - len(line.lstrip(" "))

    def _parse_config_to_tree(self, config):
        if not config:
            return None

        from anytree import Node

        root = None
        parent_node = None
        prev_node = None
        last_spaces = 0

        for line in config.splitlines():
            if line.startswith("echo") or line.startswith("#") or not line.strip():
                continue

            line_name = line.split("#", 1)[0].strip()
            spaces = self._count_spaces(line)
            if parent_node is None:
                root = Node(line_name)
                parent_node = root
                prev_node = root
            elif line_name == "exit":
                if spaces < last_spaces and parent_node.parent is not None:
                    parent_node = parent_node.parent
            elif spaces > last_spaces:
                parent_node = prev_node
                prev_node = Node(line_name, parent=prev_node)
            else:
                prev_node = Node(line_name, parent=parent_node)
            last_spaces = spaces

        return root

    def _flatten_config(self, config):
        if not config:
            return []

        from anytree import Node

        root = self._parse_config_to_tree(config)
        if root is None:
            return []

        flat_config = []
        for leaf in root.leaves:
            flat_config.append(" ".join(node.name for node in leaf.path))
        return flat_config
