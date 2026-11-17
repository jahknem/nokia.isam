# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    iter_cli_fields,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xdsl_bonding.xdsl_bonding import (
    Xdsl_bondingArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_bonding import (
    Xdsl_bondingTemplate,
)

_ROOT = "configure xdsl-bonding"
_NODE_PREFIX = re.compile(
    r"^(configure xdsl-bonding(?: board \S+ vect-fallback| group \S+| board \S+)?)(?:\s|$)"
)


class Xdsl_bondingFacts(object):
    """The isam xdsl_bonding facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Xdsl_bondingArgs.argument_spec

    def get_config(self, connection):
        """The whole resource, or only the boards/groups named in config (targeted gathering)."""
        return get_targeted_config(self._module, connection, "xdsl_bonding", "info configure xdsl-bonding", {
            "groups": "info configure xdsl-bonding group %s flat",
            "boards": "info configure xdsl-bonding board %s flat",
        })

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)
        data = unwrap_response(data)

        data = self._flatten_config(data)
        parser = Xdsl_bondingTemplate(lines=data, module=self._module)
        parsed = parser.parse()

        objs = {
            "group_assembly_time": parsed.get("group_assembly_time"),
            "ptm_init_mode": parsed.get("ptm_init_mode"),
            "groups": [parsed["groups"][key] for key in sorted(parsed.get("groups") or {})],
            "boards": [parsed["boards"][key] for key in sorted(parsed.get("boards") or {})],
        }

        ansible_facts["ansible_network_resources"].pop("xdsl_bonding", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": utils.remove_empties(objs)}, redact=True)
        )
        facts["xdsl_bonding"] = params.get("config", {})
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    def _flatten_config(self, config):
        """Flat or hierarchical output -> one canonical line per attribute.

        Defaults the device prints in detail mode (``no <attr>``) produce no line.
        Unknown keywords and sub-nodes are skipped.
        """
        flat_config = []
        if not config:
            return flat_config

        lines = []
        for raw_line in config.splitlines():
            line = raw_line.split("#", 1)[0].rstrip()
            if line.strip() and not line.strip().startswith("echo"):
                lines.append(line)

        stack = []  # prefixes of open nodes; None for a node this resource does not read
        for index, line in enumerate(lines):
            text = line.strip()
            indent = len(line) - len(line.lstrip())
            following = lines[index + 1] if index + 1 < len(lines) else None
            is_node = (
                following is not None
                and following.strip() != "exit"
                and len(following) - len(following.lstrip()) > indent
            )
            if text == "exit":
                if stack:
                    stack.pop()
                continue
            if text.startswith("configure "):
                stack = []
                full = text
            elif text == "xdsl-bonding" and not stack:
                full = _ROOT
            elif stack and stack[-1] is not None:
                full = stack[-1] + " " + text
            else:
                if is_node:
                    stack.append(None)
                continue
            if full.startswith(_ROOT + " ") or full == _ROOT:
                flat_config.extend(self._split_line(full))
            if is_node:
                match = _NODE_PREFIX.match(full)
                stack.append(match.group(1) if match else None)

        return flat_config

    @staticmethod
    def _split_line(line):
        tokens = line.split()
        if len(tokens) < 4:
            return []
        node, rest = tokens[2], tokens[3:]
        commands = []
        if node == "group-assembly-time":
            if not rest[0].isdigit():
                return []
            prefix = "configure xdsl-bonding group-assembly-time " + rest[0]
            commands.append(prefix)
            for negate, key, value in iter_cli_fields(rest[1:], value_fields=("ptm-init-mode",)):
                if not negate and value not in (None, "mode1"):
                    commands.append(prefix + " " + key + " " + value)
        elif node == "group":
            prefix = "configure xdsl-bonding group " + rest[0]
            for negate, key, value in iter_cli_fields(
                rest[1:], bool_fields=("up",), value_fields=("group-profile", "group-rtx-profile")
            ):
                if not negate and value != "none":
                    commands.append(prefix + " " + key + ("" if value is None else " " + value))
        elif node == "board" and len(rest) > 1 and rest[1] == "vect-fallback":
            prefix = "configure xdsl-bonding board " + rest[0] + " vect-fallback"
            for negate, key, value in iter_cli_fields(
                rest[2:], value_fields=("group-profile", "group-rtx-profile")
            ):
                if not negate and value not in (None, "group-level"):
                    commands.append(prefix + " " + key + " " + value)
        return commands
