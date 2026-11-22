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
    finish_targeted_outcomes,
    get_scoped_config,
    selector_key,
    targeted_explicit,
    targeted_outcomes,
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.ethernet_onts.ethernet_onts import (
    Ethernet_ontsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ethernet_onts import (
    ETHERNET_ONT_SUBNODE_FLAGS,
    ETHERNET_ONT_SUBNODE_VALUES,
    Ethernet_ontsTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    iter_cli_fields,
)

# CLI node ('phy', 'l2', 'l2 pm-collect-ext', 'cfm') -> (value attributes, flag attributes)
_SUBNODES = {}
for _path, _node, _field, _cli, _value_re, _default in ETHERNET_ONT_SUBNODE_VALUES:
    _SUBNODES.setdefault(_node, ([], []))[0].append(_cli)
for _path, _node, _field, _cli in ETHERNET_ONT_SUBNODE_FLAGS:
    _SUBNODES.setdefault(_node, ([], []))[1].append(_cli)


class Ethernet_ontsFacts(object):
    """The isam ethernet_onts facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Ethernet_ontsArgs.argument_spec

    def get_config(self, connection):
        """The whole resource, or only the ONTs named in config (targeted gathering)."""
        config = self._module.params.get("config") or []
        collector = targeted_outcomes(self._module, "ethernet_onts")
        commands = []
        selectors = {}
        for item in config:
            uni_idx = item["uni_idx"]
            command = "info configure ethernet ont %s flat detail" % uni_idx
            commands.append(command)
            selectors[command] = selector_key(uni_idx)
        data = get_scoped_config(
            self._module,
            connection,
            config,
            "info configure ethernet ont flat",
            commands,
            outcomes=collector,
            selectors=selectors,
            # An explicit gathered request that names instances must not silently widen
            # to the whole-family read when none of them became a read command.
            require_targeted=targeted_explicit(self._module, "config"),
        )
        finish_targeted_outcomes(self._module, collector)
        return data

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate the facts for Ethernet_onts network resource."""
        facts = {}

        if not data:
            data = self.get_config(connection)
        data = unwrap_response(data)
        data = self._flatten_config(data)

        ethernet_onts_parser = Ethernet_ontsTemplate(lines=data, module=self._module)
        objs = [self._drop_subnode_defaults(obj) for obj in ethernet_onts_parser.parse().values()]

        ansible_facts["ansible_network_resources"].pop("ethernet_onts", None)
        params = utils.remove_empties(
            ethernet_onts_parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )

        facts["ethernet_onts"] = params.get("config", [])
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    @staticmethod
    def _drop_subnode_defaults(obj):
        """Sub-node attributes printed with their device default value are not reported."""
        for path, _node, field, _cli, _value_re, default in ETHERNET_ONT_SUBNODE_VALUES:
            node = obj
            for key in path.split("."):
                node = node.get(key) if isinstance(node, dict) else None
            if isinstance(node, dict) and field in node and str(node[field]) == str(default):
                node.pop(field)
        return obj

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
            subnode = self._split_subnode_line(line.split()) if line.startswith("configure ethernet ont ") else None
            if subnode is not None:
                flat_config.extend(subnode)
            elif line.startswith("configure ethernet ont "):
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

    @staticmethod
    def _split_subnode_line(tokens):
        """'configure ethernet ont <uni> l2 no pm tca enable ...' -> one line per set attribute.

        None when the line is not a sub-node line. 'no <attr>' (the default) gives no line;
        unknown keywords are skipped.
        """
        if len(tokens) < 5 or tokens[4] not in ("phy", "l2", "cfm"):
            return None
        node_len = 6 if tokens[4] == "l2" and len(tokens) > 5 and tokens[5] == "pm-collect-ext" else 5
        node = " ".join(tokens[4:node_len])
        values, flags = _SUBNODES.get(node, ((), ()))
        prefix = " ".join(tokens[:node_len])
        return [
            prefix + " " + key + ("" if value is None else " " + value)
            for negate, key, value in iter_cli_fields(tokens[node_len:], bool_fields=flags, value_fields=values)
            if not negate
        ]

    def _split_packed_line(self, line):
        try:
            tokens = shlex.split(line)
        except ValueError:
            return [line]
        subnode = self._split_subnode_line(tokens)
        if subnode is not None:
            return subnode
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
