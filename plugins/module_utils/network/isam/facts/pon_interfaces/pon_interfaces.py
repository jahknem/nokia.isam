# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from anytree import Node
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_scoped_config,
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.pon_interfaces.pon_interfaces import Pon_interfacesArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.pon_interfaces import Pon_interfacesTemplate


class Pon_interfacesFacts(object):
    """The isam pon_interfaces facts class."""

    _PACKED_WORDS = {
        "label",
        "ber-calc-period",
        "polling-period",
        "sig-degrade-th",
        "sig-fail-th",
        "fec-dn",
        "raman-reduct",
        "closest-ont",
        "diff-reach",
        "pon-tag",
        "pon-id",
        "mcast-encrypt",
        "auth-method",
        "ponid-interval",
        "ponid-odn",
        "ponid-identifier",
        "max-ranging-onts",
        "tconts-per-frame",
        "admin-state",
        "pon-speed",
        "burst-overhead",
        "onu-prov-mode",
        "tc-layer",
        "tc-layer-threshold",
        "mcast-tc-layer",
        "phy-layer",
        "fec-tc-layer",
        "xg-tc-layer",
        "otdr",
        "utilization",
        "deact-ont-tca",
        "threshold",
        "threshold-percent",
        "threshold-number",
        "error-frags-up",
        "pm-collect",
        "pon-pmcollect",
        "ont-pmcollect",
        "ontbulk-pmcollect",
        "monitor-interval",
        "mode",
        "high",
        "high-clr",
        "low",
        "low-clr",
        "txmcutilhi",
        "txmcutilmd",
        "txmcutillo",
        "txtotutilhi",
        "txtotutilmd",
        "txtotutillo",
        "rxtotutilhi",
        "rxtotutilmd",
        "rxtotutillo",
        "dbacongperiodhi",
        "dbacongperiodmd",
        "dbacongperiodlo",
        "txucdropfrmhi",
        "txucdropfrmmd",
        "txucdropfrmlo",
        "txmcdropfrmhi",
        "txmcdropfrmmd",
        "txmcdropfrmlo",
        "txbcdropfrmhi",
        "txbcdropfrmmd",
        "txbcdropfrmlo",
        "rxtotdropfrmhi",
        "rxtotdropfrmmd",
        "rxtotdropfrmlo",
        "numtcint",
        "numtcintdba",
        "dbacongthresh",
    }

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Pon_interfacesArgs.argument_spec

    def get_config(self, connection):
        config = self._module.params.get("config") or []
        commands = [
            "info configure pon interface %s flat detail" % item["name"]
            for item in config
        ]
        return get_scoped_config(
            self._module,
            connection,
            config,
            "info configure pon interface flat",
            commands,
        )

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
        for entry in facts["pon_interfaces"]:
            if entry.get("pon_tag") in (0, "0"):
                entry["pon_tag"] = "0000000000000000"
            if entry.get("pon_id") in (0, "0"):
                entry["pon_id"] = "00000000"
            if entry.get("ponid_identifier") in (0, "0"):
                entry["ponid_identifier"] = "00000000000000"
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
            flat_config = []
            for line in lines:
                if line.startswith("configure pon interface "):
                    flat_config.extend(self._split_packed_line(line))
            return flat_config
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

    def _split_packed_line(self, line):
        """Split detail-flat interface lines into parser-sized commands."""
        tokens = line.split()
        if len(tokens) < 5:
            return [line]

        nested_sections = {
            "tc-layer-threshold",
            "mcast-tc-layer",
            "phy-layer",
            "fec-tc-layer",
            "xg-tc-layer",
            "otdr",
            "utilization",
            "deact-ont-tca",
        }
        section_indexes = [
            index for index, token in enumerate(tokens[4:], 4) if token in nested_sections
        ]
        if section_indexes:
            commands = []
            threshold_fields = {
                "txmcutilhi", "txmcutilmd", "txmcutillo", "txtotutilhi", "txtotutilmd",
                "txtotutillo", "rxtotutilhi", "rxtotutilmd", "rxtotutillo", "dbacongperiodhi",
                "dbacongperiodmd", "dbacongperiodlo", "txucdropfrmhi", "txucdropfrmmd",
                "txucdropfrmlo", "txmcdropfrmhi", "txmcdropfrmmd", "txmcdropfrmlo",
                "txbcdropfrmhi", "txbcdropfrmmd", "txbcdropfrmlo", "rxtotdropfrmhi",
                "rxtotdropfrmmd", "rxtotdropfrmlo", "numtcint", "numtcintdba", "dbacongthresh",
            }

            def add_fields(prefix, body, fields):
                for index, token in enumerate(body):
                    if token not in fields:
                        continue
                    start = index - 1 if index and body[index - 1] == "no" else index
                    end = index + 1 if start != index else index + 2
                    commands.append(tokens[:4] + prefix + body[start:end])

            for position, section_index in enumerate(section_indexes):
                end = section_indexes[position + 1] if position + 1 < len(section_indexes) else len(tokens)
                section = tokens[section_index:end]
                name = section[0]
                body = section[1:]
                if name == "utilization" and "threshold" in body:
                    threshold_index = body.index("threshold")
                    add_fields([name], body[:threshold_index], {"pon-pmcollect", "ont-pmcollect", "ontbulk-pmcollect"})
                    add_fields([name, "threshold"], body[threshold_index + 1:], threshold_fields)
                elif name == "utilization":
                    add_fields([name], body, {"pon-pmcollect", "ont-pmcollect", "ontbulk-pmcollect"} | threshold_fields)
                elif name == "deact-ont-tca":
                    subbranches = [
                        index for index, token in enumerate(body)
                        if token in ("threshold-percent", "threshold-number")
                    ]
                    direct_end = subbranches[0] if subbranches else len(body)
                    add_fields([name], body[:direct_end], {"mode", "monitor-interval"})
                    for subposition, subindex in enumerate(subbranches):
                        subend = subbranches[subposition + 1] if subposition + 1 < len(subbranches) else len(body)
                        add_fields([name, body[subindex]], body[subindex + 1:subend], {"high", "high-clr", "low", "low-clr"})
                else:
                    add_fields([name], body, {"pm-collect", "mode", "error-frags-up"})
            return [" ".join(command) for command in commands]

        starts = [
            index
            for index, token in enumerate(tokens[4:], 4)
            if (token in self._PACKED_WORDS and (index == 4 or tokens[index - 1] != "no"))
            or (token == "no" and index + 1 < len(tokens) and tokens[index + 1] in self._PACKED_WORDS)
        ]
        if not starts:
            return [line]

        prefix = " ".join(tokens[:4])
        return [
            prefix + " " + " ".join(tokens[start:end])
            for start, end in zip(starts, starts[1:] + [len(tokens)])
        ]
