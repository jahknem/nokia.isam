# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import re

__metaclass__ = type

from anytree import Node
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_scoped_config,
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.qos_interfaces.qos_interfaces import Qos_interfacesArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_interfaces import Qos_interfacesTemplate


class Qos_interfacesFacts(object):
    """The isam qos_interfaces facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Qos_interfacesArgs.argument_spec

    def get_config(self, connection):
        config = self._module.params.get("config") or []
        commands = [
            "info configure qos interface %s flat" % item["name"]
            for item in config
        ]
        return get_scoped_config(
            self._module,
            connection,
            config,
            "info configure qos interface flat",
            commands,
        )

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)
        data = unwrap_response(data)
        data = self._flatten_config(data)

        parser = Qos_interfacesTemplate(lines=data, module=self._module)
        objs = list(parser.parse().values())

        for item in objs:
            for key in ["queue", "upstream_queue", "ds_rem_queue"]:
                if isinstance(item.get(key), dict):
                    item[key] = list(item[key].values())

        ansible_facts["ansible_network_resources"].pop("qos_interfaces", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )
        facts["qos_interfaces"] = params.get("config", [])
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts

    def _count_spaces(self, line):
        return len(line) - len(line.lstrip(" "))

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

            stripped = line.split("#", 1)[0].strip()
            if not stripped:
                continue

            if parent_node is None:
                root = Node(stripped)
                parent_node = root
                prev_node = root
            elif stripped == "exit":
                if self._count_spaces(line) < last_spaces and parent_node.parent:
                    parent_node = parent_node.parent
                else:
                    continue
            elif self._count_spaces(line) > last_spaces:
                parent_node = prev_node
                prev_node = Node(stripped, parent=prev_node)
            else:
                prev_node = Node(stripped, parent=parent_node)

            last_spaces = self._count_spaces(line)
        return root

    def _flatten_config(self, config):
        if not config:
            return []
        lines = [
            line.strip()
            for line in config.splitlines()
            if line.strip() and not line.strip().startswith("#") and not line.strip().startswith("echo")
        ]
        if lines and all(line.startswith("configure qos interface") for line in lines):
            return self._compact_lines(lines)
        root = self._parse_config_to_tree(config)
        if root is None:
            return []
        flat_config = []
        for leaf in root.leaves:
            line = []
            for node in leaf.path:
                line.append(node.name)
            flat_config.append(" ".join(line))
        return flat_config

    @staticmethod
    def _compact_lines(lines):
        clauses = re.compile(
            r"(?:scheduler-node|ingress-profile|cac-profile|ext-cac|ds-queue-sharing|"
            r"us-queue-sharing|ds-num-queue|ds-num-rem-queue|"
            r"oper-weight|oper-rate|dsfld-shaper-prof|"
            r"bandwidth-profile|bandwidth-sharing|aggr-usq-profile|aggr-dsq-profile|"
            r"gem-sharing|scheduler-mode|mc-scheduler-node|bc-scheduler-node|ds-schedule-tag)\s+\S+|"
            r"(?:no\s+)?(?:queue-stats-on|autoschedule|us-vlanport-queue)(?=\s|$)|"
            r"(?:queue|upstream-queue|ds-rem-queue)\s+\d+\s+(?:priority|weight|oper-weight|"
            r"queue-profile|shaper-profile|bandwidth-profile|ext-bw|bandwidth-sharing)\s+\S+"
        )
        result = []
        for line in lines:
            match = re.match(r"(configure qos interface\s+\S+\s+)(.*)", line)
            if not match:
                result.append(line)
                continue
            result.extend(match.group(1) + clause.group(0) for clause in clauses.finditer(match.group(2)))
        return result
