# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xstp.xstp import (
    XstpArgs,
)


class XstpFacts(object):
    """The isam xstp facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = XstpArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = connection.get("info configure xstp flat")

        xstp_config = self._parse_xstp_config(data)

        ansible_facts["ansible_network_resources"].pop("xstp", None)
        facts["xstp"] = utils.remove_empties(xstp_config) or {}
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    def _parse_xstp_config(self, config):
        xstp = {"general": {}, "ports": []}
        ports = {}
        section = None
        current_port = None

        for raw_line in config.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith("echo "):
                continue

            if line.startswith("configure xstp "):
                self._parse_flat_line(line, xstp, ports)
                continue

            if line == "general":
                section = "general"
                current_port = None
                continue
            if line.startswith("port "):
                section = "port"
                current_port = line.split(None, 1)[1]
                ports.setdefault(current_port, {"port": current_port})
                continue
            if line == "exit":
                section = None
                current_port = None
                continue

            if section == "general":
                self._parse_general_option(line, xstp["general"])
            elif section == "port" and current_port:
                self._parse_port_option(line, ports[current_port])

        xstp["ports"] = sorted(ports.values(), key=lambda item: item.get("port", ""))
        return xstp

    def _parse_flat_line(self, line, xstp, ports):
        parts = line.split()
        if len(parts) < 4:
            return
        if parts[2] == "general":
            self._parse_general_option(" ".join(parts[3:]), xstp["general"])
            return
        if parts[2] == "port" and len(parts) >= 5:
            port = parts[3]
            entry = ports.setdefault(port, {"port": port})
            self._parse_port_option(" ".join(parts[4:]), entry)

    def _parse_general_option(self, line, general):
        if line == "enable-stp":
            general["enable_stp"] = True
        elif line == "no enable-stp":
            general["enable_stp"] = False
        elif line.startswith("region-name "):
            general["region_name"] = line.split(None, 1)[1].strip('"')

    def _parse_port_option(self, line, port):
        if line.startswith("path-cost "):
            value = line.split(None, 1)[1]
            try:
                port["path_cost"] = int(value)
            except ValueError:
                pass
