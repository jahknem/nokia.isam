# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam xdsl_lines fact class.
"""

from anytree import Node
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xdsl_lines.xdsl_lines import (
    Xdsl_linesArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_lines import (
    Xdsl_linesTemplate,
)


class Xdsl_linesFacts(object):
    """The isam xdsl_lines facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Xdsl_linesArgs.argument_spec

    def get_config(self, connection):
        """Wrapper method for `connection.get()` used by unit tests."""
        return connection.get("info configure xdsl line")

    @staticmethod
    def _canonicalize_entry(item):
        entry = dict(item)
        if "if_index" in entry and "name" not in entry:
            entry["name"] = entry["if_index"]
        for dashed, underscored in (
            ("service-profile", "service_profile"),
            ("spectrum-profile", "spectrum_profile"),
            ("dpbo-profile", "dpbo_profile"),
            ("vect-profile", "vect_profile"),
            ("admin-up", "admin_up"),
        ):
            if dashed in entry and underscored not in entry:
                entry[underscored] = entry[dashed]
            entry.pop(dashed, None)
        entry.pop("if_index", None)
        return entry

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate facts for the xdsl_lines network resource."""
        facts = {}
        if not data:
            data = self.get_config(connection)
        if isinstance(data, tuple):
            data = data[0]

        data = self._flatten_config(data)
        xdsl_lines_parser = Xdsl_linesTemplate(lines=data, module=self._module)
        objs = [self._canonicalize_entry(item) for item in xdsl_lines_parser.parse().values()]

        ansible_facts["ansible_network_resources"].pop("xdsl_lines", None)
        params = utils.remove_empties(
            xdsl_lines_parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        ) or {}
        facts["xdsl_lines"] = [
            self._canonicalize_entry(item) for item in params.get("config") or []
        ]
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    @staticmethod
    def _count_spaces(line):
        return len(line) - len(line.lstrip(" "))

    def _parse_config_to_tree(self, config):
        if not config:
            return None

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
        root = self._parse_config_to_tree(config)
        if root is None:
            return []

        flat_config = []
        for leaf in root.leaves:
            flat_config.append(" ".join(node.name for node in leaf.path))
        return flat_config
