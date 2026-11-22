# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.interface_alarms.interface_alarms import (
    Interface_alarmsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_whole_node_targeted,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.interface_alarms import (
    Interface_alarmsTemplate,
)


class Interface_alarmsFacts(object):
    """The isam interface_alarms facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Interface_alarmsArgs.argument_spec

    def get_config(self, connection):
        """The whole node, read once; per-instance outcomes for a targeted request.

        The device has no single-instance read here: it only answers the whole
        node, with flat 'configure interface alarm <name> ...' lines (or a
        'configure interface' header + 'alarm <name>' blocks). An explicit
        targeted request (state gathered, config names alarms) reads the node
        once and reports per-instance read_outcomes from the parsed catalog
        (get_whole_node_targeted): present when the catalog lists the alarm,
        unknown when it does not. The gathered string stays the full catalog,
        unfiltered.
        """
        return get_whole_node_targeted(
            self._module, connection, "interface_alarms", "info configure interface alarm",
            ("config",), lambda data: self._parse_catalog(data)[0],
        )

    @staticmethod
    def _canonicalize_entry(item):
        return dict(item)

    def _parse_catalog(self, data):
        """The parsed full catalog: (one entry per configured alarm, its parser)."""
        if isinstance(data, tuple):
            data = data[0]
        lines = self._flatten_config(data)
        parser = Interface_alarmsTemplate(lines=lines, module=self._module)
        entries = [self._canonicalize_entry(item) for item in parser.parse().values()]
        return entries, parser

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)

        objs, parser = self._parse_catalog(data)

        ansible_facts["ansible_network_resources"].pop("interface_alarms", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        ) or {}
        facts["interface_alarms"] = [
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

        config = self._join_header(config)
        flat_config = []
        for block in self._top_level_blocks(config):
            root = self._parse_config_to_tree(block)
            if root is None:
                continue
            for leaf in root.leaves:
                flat_config.append(" ".join(node.name for node in leaf.path))
        return flat_config

    @staticmethod
    def _join_header(config):
        """The device answers 'configure interface' + 'alarm <name>' blocks; join them.

        Flat lines ('configure interface alarm <name> ...') pass through unchanged.
        """
        lines = []
        header = None
        for line in config.splitlines():
            stripped = line.split("#", 1)[0].strip()
            if not stripped or stripped.startswith("echo") or stripped == "exit":
                continue
            if stripped == "configure interface":
                header = stripped
                continue
            if header and stripped.startswith("alarm "):
                lines.append(header + " " + stripped)
                continue
            if header and line[:1].isspace() and lines:
                lines[-1] += " " + stripped
                continue
            lines.append(line)
        return "\n".join(lines)

    @staticmethod
    def _top_level_blocks(config):
        """Split output into its top-level blocks.

        Each unindented line (e.g. one per alarm, or one per targeted read)
        starts its own tree, so blocks are not nested into each other.
        """
        blocks = []
        for line in config.splitlines():
            if line.startswith("echo") or line.startswith("#") or not line.strip():
                continue
            if not line[:1].isspace() and line.split("#", 1)[0].strip() != "exit":
                blocks.append([])
            if blocks:
                blocks[-1].append(line)
        return ["\n".join(block) for block in blocks]
