# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import shlex

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xstp.xstp import (
    XstpArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xstp import (
    XSTP_GENERAL_FIELDS,
    XSTP_PORT_FIELDS,
    XSTP_PORT_FLAGS,
    XstpTemplate,
)

_GENERAL_BY_CLI = dict((spec[0], (field, spec[2], spec[1])) for field, spec in XSTP_GENERAL_FIELDS.items())
_PORT_BY_CLI = dict((spec[0], (field, spec[2], spec[1])) for field, spec in XSTP_PORT_FIELDS.items())
_PORT_FLAG_BY_CLI = dict((cli, field) for field, cli in XSTP_PORT_FLAGS.items())


def _set_value(target, field, kind, raw, default):
    """Store a CLI value unless it is the device default; a value that does not fit the type is skipped."""
    try:
        value = kind(raw)
    except ValueError:
        return
    if value != default:
        target[field] = value


class XstpFacts(object):
    """The isam xstp facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = XstpArgs.argument_spec

    def get_config(self, connection):
        """The whole resource, or only the ports named in config (targeted gathering)."""
        return get_targeted_config(self._module, connection, "xstp", "info configure xstp flat", {
            "ports": "info configure xstp port %s flat",
        })

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)
        data = unwrap_response(data) or ""

        xstp_config = utils.remove_empties(self._parse_xstp_config(data))

        ansible_facts["ansible_network_resources"].pop("xstp", None)
        params = {}
        if xstp_config:
            params = utils.remove_empties(
                XstpTemplate(lines=[], module=self._module).validate_config(
                    self.argument_spec, {"config": xstp_config}, redact=True,
                )
            )
        facts["xstp"] = params.get("config") or {}
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
                # 'port <port> [<option> <value> ...]' opens the port block; inline options are parsed too.
                section = "port"
                parts = line.split(None, 2)
                current_port = parts[1]
                ports.setdefault(current_port, {"port": current_port})
                if len(parts) > 2:
                    self._parse_port_option(parts[2], ports[current_port])
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
        if parts[2] == "port":
            # 'configure xstp port <port>' without options: the port exists with defaults.
            port = parts[3]
            entry = ports.setdefault(port, {"port": port})
            self._parse_port_option(" ".join(parts[4:]), entry)

    @staticmethod
    def _tokens(line):
        try:
            return shlex.split(line)
        except ValueError:
            return line.split()

    def _parse_general_option(self, line, general):
        """One or several general options, e.g. 'enable-stp region-name 00:00:5e:00:53:01'."""
        tokens = self._tokens(line)
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token == "enable-stp":
                general["enable_stp"] = True
            elif token == "no" and index + 1 < len(tokens) and tokens[index + 1] == "enable-stp":
                general["enable_stp"] = False
                index += 1
            elif token == "region-name" and index + 1 < len(tokens):
                general["region_name"] = tokens[index + 1]
                index += 1
            elif token == "no" and index + 1 < len(tokens) and tokens[index + 1] in _GENERAL_BY_CLI:
                index += 1  # 'no <attr>': the device default, not reported
            elif token in _GENERAL_BY_CLI and index + 1 < len(tokens):
                field, kind, default = _GENERAL_BY_CLI[token]
                _set_value(general, field, kind, tokens[index + 1], default)
                index += 1
            index += 1

    def _parse_port_option(self, line, port):
        """One or several port options, e.g. 'path-cost 200000' (unknown options are skipped).

        Defaults printed in detail mode ('no priority', 'no edge-port', ...) are not reported.
        """
        tokens = self._tokens(line)
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token == "path-cost" and index + 1 < len(tokens):
                try:
                    port["path_cost"] = int(tokens[index + 1])
                except ValueError:
                    pass
                index += 1
            elif token == "no" and index + 1 < len(tokens) and (
                tokens[index + 1] in _PORT_BY_CLI or tokens[index + 1] in _PORT_FLAG_BY_CLI
            ):
                index += 1
            elif token in _PORT_FLAG_BY_CLI:
                port[_PORT_FLAG_BY_CLI[token]] = True
            elif token in _PORT_BY_CLI and index + 1 < len(tokens):
                field, kind, default = _PORT_BY_CLI[token]
                _set_value(port, field, kind, tokens[index + 1], default)
                index += 1
            index += 1
