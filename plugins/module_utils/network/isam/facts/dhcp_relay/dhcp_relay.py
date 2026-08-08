# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.dhcp_relay.dhcp_relay import Isam_dhcp_relayArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import unwrap_response
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.dhcp_relay import Isam_dhcp_relayTemplate


class Isam_dhcp_relayFacts(object):
    """The isam_dhcp_relay facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Isam_dhcp_relayArgs.argument_spec

    def get_config(self, connection):
        return connection.get("info configure dhcp-relay flat")

    def populate_facts(self, connection, ansible_facts, data=None):
        data = unwrap_response(data if data else self.get_config(connection))
        parser = Isam_dhcp_relayTemplate(lines=self._flatten_config(data), module=self._module)
        objs = list(parser.parse().values())
        ansible_facts["ansible_network_resources"].pop("isam_dhcp_relay", None)
        params = utils.remove_empties(parser.validate_config(self.argument_spec, {"config": objs}, redact=True)) or {}
        ansible_facts["ansible_network_resources"]["isam_dhcp_relay"] = params.get("config") or []
        return ansible_facts

    def _flatten_config(self, config):
        lines = []
        in_relay = False
        for raw_line in (config or "").splitlines():
            line = raw_line.split("#", 1)[0].rstrip()
            stripped = line.strip()
            if not stripped or stripped.startswith(("echo", "#")):
                continue
            if line.startswith("configure dhcp-relay "):
                lines.append(line)
            elif stripped in ("dhcp-relay", "configure dhcp-relay"):
                in_relay = True
            elif stripped == "exit":
                in_relay = False
            elif in_relay and stripped.startswith(("port-stats ", "no port-stats ", "v6-port-stats ", "no v6-port-stats ")):
                lines.append("configure dhcp-relay " + stripped)
        return lines
