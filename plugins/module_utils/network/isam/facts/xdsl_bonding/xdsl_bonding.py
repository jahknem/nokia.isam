# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xdsl_bonding.xdsl_bonding import (
    Xdsl_bondingArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_bonding import (
    Xdsl_bondingTemplate,
)


class Xdsl_bondingFacts(object):
    """The isam xdsl_bonding facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Xdsl_bondingArgs.argument_spec

    def get_config(self, connection):
        return connection.get("info configure xdsl-bonding")

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
        }

        ansible_facts["ansible_network_resources"].pop("xdsl_bonding", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )
        facts["xdsl_bonding"] = params.get("config", {})
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    def _flatten_config(self, config):
        flat_config = []
        if not config:
            return flat_config

        current = None
        in_xdsl_bonding = False

        for raw_line in config.splitlines():
            line = raw_line.split("#", 1)[0].rstrip()
            stripped = line.strip()
            if not stripped or stripped.startswith("echo") or stripped.startswith("#"):
                continue

            if line.startswith("configure xdsl-bonding group-assembly-time"):
                flat_config.append(line)
                continue

            if line.startswith("configure xdsl-bonding"):
                in_xdsl_bonding = True
                current = "configure xdsl-bonding"
                continue
            if stripped == "xdsl-bonding":
                in_xdsl_bonding = True
                current = "configure xdsl-bonding"
                continue
            if stripped == "exit":
                current = None
                continue
            if not in_xdsl_bonding:
                continue

            if current and stripped.startswith("group-assembly-time"):
                flat_config.append(current + " " + stripped)

        return flat_config
