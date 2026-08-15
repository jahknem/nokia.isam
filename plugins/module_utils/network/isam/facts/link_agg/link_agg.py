# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from anytree import Node

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.link_agg.link_agg import (
    Link_aggArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    iter_cli_fields,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.link_agg import (
    Link_aggTemplate,
)


class Link_aggFacts(object):
    """The isam link_agg facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Link_aggArgs.argument_spec

    def get_config(self, connection):
        return connection.get("info configure link-agg flat")

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)
        data = unwrap_response(data)

        data = self._flatten_config(data)
        parser = Link_aggTemplate(lines=data, module=self._module)
        parsed = parser.parse().values()

        obj = {"ports": [], "groups": []}
        for item in parsed:
            item_type = item.pop("type", None)
            if item_type == "port":
                self._normalize_port(item)
                obj["ports"].append(item)
            elif item_type == "group":
                if isinstance(item.get("ports"), dict):
                    item["ports"] = sorted(item["ports"].values())
                obj["groups"].append(item)

        ansible_facts["ansible_network_resources"].pop("link_agg", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": obj}, redact=True)
        )
        facts["link_agg"] = params.get("config", {})
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    def _normalize_port(self, port):
        if "passive_lacp" in port:
            port["lacp_mode"] = "passive" if port["passive_lacp"] else "active"
        if "short_timeout" in port:
            port["timeout"] = "short" if port["short_timeout"] else "long"

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
            if line.startswith("echo") or line.startswith("#") or not line.strip():
                continue

            if parent_node is None:
                root = Node(line.split("#", 1)[0].strip())
                parent_node = root
                prev_node = root
            elif line.strip() == "exit":
                if self._count_spaces(line) < last_spaces and parent_node.parent:
                    parent_node = parent_node.parent
                last_spaces = self._count_spaces(line)
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
            return []

        lines = [line.strip() for line in config.splitlines() if line.strip()]
        if any(line.startswith("configure link-agg") for line in lines):
            return self._split_flat_lines(lines)

        root = self._parse_config_to_tree(config)
        if root is None:
            return []

        flat_config = []
        for leaf in root.leaves:
            line = []
            for node in leaf.path:
                line.append(node.name)
            rendered = " ".join(line)
            if rendered.startswith("configure link-agg"):
                flat_config.append(rendered)
        return self._split_flat_lines(flat_config)

    def _split_flat_lines(self, lines):
        split_lines = []
        for line in lines:
            parts = line.split()
            if len(parts) < 5 or parts[0:2] != ["configure", "link-agg"]:
                continue
            if parts[2] == "port":
                split_lines.extend(self._split_port_line(parts))
            elif parts[2] == "group":
                split_lines.extend(self._split_group_line(parts))
        return split_lines

    def _split_port_line(self, parts):
        port_id = parts[3]
        lines = []
        for negate, key, value in iter_cli_fields(
            parts[4:],
            bool_fields=("passive-lacp", "short-timeout"),
            value_fields=("actor-port-prio",),
        ):
            if value is None:
                lines.append("configure link-agg port {0} {1}{2}".format(port_id, "no " if negate else "", key))
            else:
                lines.append("configure link-agg port {0} {1} {2}".format(port_id, key, value))
        return lines

    def _split_group_line(self, parts):
        group_id = parts[3]
        lines = []
        value_fields = [
            "load-sharing-policy",
            "max-active-port",
            "swo-threshold",
            "priority",
            "swo-revert",
            "mode",
            "master-iwf",
            "port",
        ]
        for negate, key, value in iter_cli_fields(
            parts[4:],
            value_fields=value_fields,
            negated_value_fields=("port",),
        ):
            if value is None:
                lines.append("configure link-agg group {0} no {1}".format(group_id, key))
            else:
                lines.append("configure link-agg group {0} {1}{2} {3}".format(group_id, "no " if negate else "", key, value))
        return lines
