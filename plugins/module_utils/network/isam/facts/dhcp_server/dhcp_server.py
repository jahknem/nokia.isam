# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.dhcp_server.dhcp_server import (
    Isam_dhcp_serverArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.dhcp_server import (
    Isam_dhcp_serverTemplate,
)


class Isam_dhcp_serverFacts(object):
    """The isam_dhcp_server facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Isam_dhcp_serverArgs.argument_spec

    def get_config(self, connection):
        return connection.get("info configure dhcp-server")

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)
        if type(data) == tuple:
            data = data[0]

        data = self._flatten_config(data)
        parser = Isam_dhcp_serverTemplate(lines=data, module=self._module)
        parsed = parser.parse()

        objs = {
            "start_addr": parsed.get("start_addr"),
            "end_addr": parsed.get("end_addr"),
            "subnet_mask": parsed.get("subnet_mask"),
            "lease_time": int(parsed["lease_time"]) if parsed.get("lease_time") else None,
        }

        ansible_facts["ansible_network_resources"].pop("isam_dhcp_server", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )
        facts["isam_dhcp_server"] = params.get("config", {})
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    def _flatten_config(self, config):
        flat_config = []
        if not config:
            return flat_config

        in_dhcp_server = False

        for raw_line in config.splitlines():
            line = raw_line.split("#", 1)[0].rstrip()
            stripped = line.strip()
            if not stripped or stripped.startswith("echo") or stripped.startswith("#"):
                continue

            if line.startswith("configure dhcp-server "):
                flat_config.append(line)
                continue

            if stripped == "dhcp-server":
                in_dhcp_server = True
                continue
            if stripped == "exit":
                in_dhcp_server = False
                continue
            if not in_dhcp_server:
                continue

            if line == stripped and stripped.startswith(("start-addr ", "end-addr ", "subnet-mask ", "lease-time ")):
                flat_config.append("configure dhcp-server " + stripped)

        return flat_config
