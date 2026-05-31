# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.system.system import (
    Isam_systemArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.system import (
    Isam_systemTemplate,
)


class Isam_systemFacts(object):
    """The isam system facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Isam_systemArgs.argument_spec

    def get_config(self, connection):
        return connection.get("info configure system flat")

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)
        if type(data) == tuple:
            data = data[0]

        lines = [l.strip() for l in data.splitlines() if l.strip() and not l.startswith("#") and not l.startswith("echo")]
        parser = Isam_systemTemplate(lines=lines, module=self._module)
        parsed = parser.parse()

        objs = {
            "id": parsed.get("id", {}),
            "security": parsed.get("security", {}),
            "sntp": parsed.get("sntp", {}),
            "syslog": parsed.get("syslog", {}),
            "sync_if_timing": parsed.get("sync_if_timing", {}),
            "transaction": parsed.get("transaction", {}),
        }

        ansible_facts["ansible_network_resources"].pop("system", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )
        facts["system"] = params.get("config", {})
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts
