# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam ethernet_onts fact class.
"""

from anytree import Node
import shlex
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_scoped_config,
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.ethernet_onts.ethernet_onts import (
    Ethernet_ontsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ethernet_onts import (
    Ethernet_ontsTemplate,
)


class Ethernet_ontsFacts(object):
    """The isam ethernet_onts facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Ethernet_ontsArgs.argument_spec

    def get_config(self, connection):
        """Wrapper method for `connection.get()`."""
        config = self._module.params.get("config") or []
        commands = [
            "info configure ethernet ont %s flat detail" % item["uni_idx"]
            for item in config
        ]
        return get_scoped_config(
            self._module,
            connection,
            config,
            "info configure ethernet ont flat",
            commands,
        )

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate the facts for Ethernet_onts network resource."""
        facts = {}

        if not data:
            data = self.get_config(connection)
        data = unwrap_response(data)
        data = self._flatten_config(data)

        ethernet_onts_parser = Ethernet_ontsTemplate(lines=data, module=self._module)
        objs = list(ethernet_onts_parser.parse().values())

        ansible_facts["ansible_network_resources"].pop("ethernet_onts", None)
        params = utils.remove_empties(
            ethernet_onts_parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )

        facts["ethernet_onts"] = params.get("config", [])
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    def _count_spaces(self, line):
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
            if parent_node is None:
                root = Node(line.split("#", 1)[0].strip())
                parent_node = root
                prev_node = root
            elif line.strip() == "exit":
                if self._count_spaces(line) < last_spaces and parent_node.parent:
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
        flat_lines = []
        for raw_line in config.splitlines():
            line = raw_line.strip()
            if line.startswith("configure ethernet ont "):
                flat_lines.extend(self._split_packed_line(line))
        if flat_lines:
            return flat_lines

        root = self._parse_config_to_tree(config)
        if not root:
            return []
        flat_config = []
        for leaf in root.leaves:
            line = " ".join(node.name for node in leaf.path)
            if line.startswith("configure ethernet ont "):
                flat_config.append(line)
            elif line.startswith("configure "):
                flat_config.append(line)
            else:
                flat_config.append("configure ethernet " + line)
        return flat_config

    _PACKED_WORDS = {
        "cust-info", "auto-detect", "power-control", "pse-class",
        "pse-pw-priority", "pwr-override", "lpt-mode", "admin-state",
    }

    def _split_packed_line(self, line):
        try:
            tokens = shlex.split(line)
        except ValueError:
            return [line]
        starts = [
            index for index, token in enumerate(tokens[4:], 4)
            if (token in self._PACKED_WORDS and (index == 4 or tokens[index - 1] != "no"))
            or (token == "no" and index + 1 < len(tokens) and tokens[index + 1] in self._PACKED_WORDS)
        ]
        if not starts:
            return [line]
        prefix = " ".join(tokens[:4])
        result = []
        for start, end in zip(starts, starts[1:] + [len(tokens)]):
            segment = tokens[start:end]
            if segment and segment[0] == "cust-info" and len(segment) > 1:
                segment = [segment[0], '"' + " ".join(segment[1:]) + '"']
            result.append(prefix + " " + " ".join(segment))
        return result
