# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam ntp_onts fact class.
"""

from anytree import Node
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.ntp_onts.ntp_onts import (
    Ntp_ontsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ntp_onts import (
    Ntp_ontsTemplate,
)


class Ntp_ontsFacts(object):
    """The isam ntp_onts facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Ntp_ontsArgs.argument_spec

    def get_config(self, connection):
        """Wrapper method for `connection.get()`."""
        return connection.get("info configure ntp")

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate the facts for Ntp_onts network resource."""
        facts = {}

        if not data:
            data = self.get_config(connection)
        if type(data) == tuple:
            data = data[0]
        data = self._flatten_config(data)

        ntp_onts_parser = Ntp_ontsTemplate(lines=data, module=self._module)
        objs = list(ntp_onts_parser.parse().values())

        ansible_facts["ansible_network_resources"].pop("ntp_onts", None)
        params = utils.remove_empties(
            ntp_onts_parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )

        facts["ntp_onts"] = params.get("config", [])
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
            if line.startswith("configure ntp ont "):
                flat_lines.append(line)
        if flat_lines:
            return flat_lines

        root = self._parse_config_to_tree(config)
        if not root:
            return []
        flat_config = []
        for leaf in root.leaves:
            line = " ".join(node.name for node in leaf.path)
            if line.startswith("configure ntp ont "):
                flat_config.append(line)
            elif line.startswith("configure ntp "):
                flat_config.append(line)
            elif line.startswith("configure "):
                flat_config.append(line)
            else:
                flat_config.append("configure ntp " + line)
        return flat_config
