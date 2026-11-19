# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.software_mngt.software_mngt import (
    Software_mngtArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.software_mngt import (
    parse_lines,
    without_defaults,
)


class Software_mngtFacts(object):
    """The isam software_mngt facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Software_mngtArgs.argument_spec

    def get_config(self, connection):
        """The whole resource, or only the OSWPs named in config (targeted gathering)."""
        return get_targeted_config(self._module, connection, "software_mngt", "info configure software-mngt flat", {
            "oswp": "info configure software-mngt oswp %s flat",
        })

    def populate_facts(self, connection, ansible_facts, data=None):
        if not data:
            data = self.get_config(connection)
        lines = self._flatten(unwrap_response(data))
        params = without_defaults(parse_lines("\n".join(lines)))
        ansible_facts["ansible_network_resources"].pop("software_mngt", None)
        ansible_facts["ansible_network_resources"]["software_mngt"] = params
        return ansible_facts

    @staticmethod
    def _flatten(config):
        lines = []
        for raw in str(config or "").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or line.startswith("echo "):
                continue
            if line.startswith("configure software-mngt "):
                lines.append(line)
        return lines
