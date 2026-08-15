# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.traps.traps import (
    Isam_trapsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    canonical_key,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.traps import (
    Isam_trapsTemplate,
    TRAP_TYPE_NAMES,
    SHAPING_FIELDS,
)


class Isam_trapsFacts(object):
    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Isam_trapsArgs.argument_spec

    def get_config(self, connection):
        return connection.get("info configure trap")

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)
        if isinstance(data, tuple):
            data = data[0]

        if not data:
            ansible_facts["ansible_network_resources"]["isam_traps"] = {}
            return ansible_facts

        flat_lines = self._flatten_config(data)
        parser = Isam_trapsTemplate(lines=flat_lines, module=self._module)
        parsed = parser.parse()

        objs = {
            "definitions": list(parsed.get("definitions", {}).values()),
            "managers": list(parsed.get("managers", {}).values()),
            "v6managers": list(parsed.get("v6managers", {}).values()),
        }

        self._cleanup_parsed(objs)

        ansible_facts["ansible_network_resources"].pop("isam_traps", None)
        params = utils.remove_empties(
            parser.validate_config(
                self.argument_spec, {"config": objs}, redact=True
            )
        )
        facts["isam_traps"] = params.get("config", {})
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    def _cleanup_parsed(self, objs):
        for entry in objs["definitions"]:
            pass
        for entry in objs["managers"]:
            for cli_name in TRAP_TYPE_NAMES:
                field = canonical_key(cli_name)
                if field in entry and entry[field] == "":
                    del entry[field]
            for field, _ in SHAPING_FIELDS:
                if field in entry and entry[field] == "":
                    del entry[field]
        for entry in objs["v6managers"]:
            for cli_name in TRAP_TYPE_NAMES:
                field = canonical_key(cli_name)
                if field in entry and entry[field] == "":
                    del entry[field]
            for field, _ in SHAPING_FIELDS:
                if field in entry and entry[field] == "":
                    del entry[field]

    def _flatten_config(self, config):
        flat_config = []
        if not config:
            return flat_config

        in_trap = False
        current_resource = None
        for raw_line in config.splitlines():
            line = raw_line.split("#", 1)[0].rstrip()
            stripped = line.strip()
            if not stripped or stripped.startswith("echo") or stripped.startswith("#"):
                continue

            if line.startswith("configure trap"):
                flat_config.append(line)
                continue

            if stripped == "trap":
                in_trap = True
                current_resource = None
                continue

            if stripped == "exit":
                if current_resource:
                    current_resource = None
                elif in_trap:
                    in_trap = False
                continue

            if not in_trap:
                continue

            leading_spaces = len(line) - len(line.lstrip())

            if current_resource and leading_spaces > 4:
                line_suffix = stripped
                flat_config.append("%s %s" % (current_resource, line_suffix))
            elif stripped.startswith("definition") or stripped.startswith("manager") or stripped.startswith("v6manager"):
                current_resource = "configure trap %s" % stripped
                flat_config.append(current_resource)

        return flat_config
