# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    unwrap_response,
    validate_config_safe,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xdsl_boards.xdsl_boards import (
    Xdsl_boardsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    parse_cli_key_values,
)


class Xdsl_boardsFacts(object):
    """The isam xdsl_boards facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Xdsl_boardsArgs.argument_spec

    def get_config(self, connection):
        return "\n".join(
            [
                unwrap_response(connection.get("info configure xdsl board flat")),
                unwrap_response(connection.get("info configure xdsl vp-board flat")),
            ]
        )

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)
        data = unwrap_response(data)

        objs = self._parse_config(data)
        ansible_facts["ansible_network_resources"].pop("xdsl_boards", None)
        params = utils.remove_empties(
            validate_config_safe(self.argument_spec, {"config": objs})
        )
        facts["xdsl_boards"] = params.get("config", {})
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts

    def _parse_config(self, config):
        result = {"boards": [], "vp_boards": []}
        current = None
        current_type = None

        if not config:
            return result

        for raw_line in config.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith("echo"):
                continue
            if line in ("configure xdsl",):
                continue
            if line.startswith("configure xdsl "):
                line = line[len("configure xdsl "):]
            if line == "exit":
                if current is not None:
                    result[current_type].append(current)
                    current = None
                    current_type = None
                continue

            parts = line.split()
            if parts[0] == "board" and len(parts) >= 2:
                if current_type == "boards" and current is not None and current.get("board_id") == parts[1]:
                    self._set_pairs(current, parts[2:])
                    continue
                if current is not None:
                    result[current_type].append(current)
                current_type = "boards"
                current = {"board_id": parts[1]}
                self._set_pairs(current, parts[2:])
            elif parts[0] == "vp-board" and len(parts) >= 2:
                if current_type == "vp_boards" and current is not None and current.get("vp_board_id") == parts[1]:
                    self._set_pairs(current, parts[2:])
                    continue
                if current is not None:
                    result[current_type].append(current)
                current_type = "vp_boards"
                current = {"vp_board_id": parts[1]}
                self._set_pairs(current, parts[2:])
            elif current is not None:
                self._set_pairs(current, parts)

        if current is not None:
            result[current_type].append(current)

        return result

    def _set_pairs(self, item, parts):
        if len(parts) >= 2 and parts[0] == "no" and parts[1] == "admin-state":
            item["admin_state"] = False
            parts = parts[2:]
        item.update(parse_cli_key_values(parts, bare_keys_as_true=True))
