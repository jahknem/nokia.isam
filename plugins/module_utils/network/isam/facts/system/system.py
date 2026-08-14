# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import shlex

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    unwrap_response,
)
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
        data = unwrap_response(data)

        lines = self._flatten_config(data)
        parser = Isam_systemTemplate(lines=lines, module=self._module)
        parsed = parser.parse()
        objs = self._parse_flat_config(lines)
        for section in ("id", "security", "sntp", "syslog", "sync_if_timing", "transaction"):
            if parsed.get(section):
                objs.setdefault(section, {}).update(parsed[section])

        ansible_facts["ansible_network_resources"].pop("system", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )
        facts["system"] = params.get("config", {})
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    def _flatten_config(self, config):
        lines = []
        in_system = False
        current_section = None

        for raw_line in config.splitlines():
            line = raw_line.split("#", 1)[0].rstrip()
            stripped = line.strip()
            if not stripped or stripped.startswith("echo") or stripped.startswith("#"):
                continue
            if stripped.startswith("configure system "):
                lines.extend(self._split_packed_syntax(stripped))
                continue
            if stripped == "configure":
                continue
            if stripped == "system":
                in_system = True
                current_section = None
                continue
            if stripped == "exit":
                if current_section:
                    current_section = None
                else:
                    in_system = False
                continue
            if not in_system:
                continue
            if stripped in ("id", "security", "sntp", "sync-if-timing", "syslog", "transaction", "max-lt-link-speed", "loop-id-syntax", "relay-id-syntax"):
                current_section = stripped
                continue
            if current_section:
                lines.append("configure system {0} {1}".format(current_section, stripped))
            else:
                lines.append("configure system " + stripped)

        return lines

    def _parse_flat_config(self, lines):
        objs = {}
        for line in lines:
            if not line.startswith("configure system "):
                continue
            try:
                tokens = shlex.split(line)
            except ValueError:
                tokens = line.split()
            if len(tokens) < 3:
                continue

            section = tokens[2]
            values = tokens[3:]

            if section == "id" and values:
                id_section = objs.setdefault("id", {})
                id_section["node_id"] = values[0]
                self._copy_token_value(values, "name", id_section, "name")
                self._copy_token_value(values, "location", id_section, "location")
                self._copy_token_value(values, "contact-person", id_section, "contact")
                self._copy_token_value(values, "nt-intercon-vlan", id_section, "nt_intercon_vlan", int)
                self._copy_token_value(values, "internal-nw-vlan", id_section, "internal_nw_vlan", int)
                self._copy_token_value(values, "system-mac", id_section, "system_mac")
            elif section == "sntp":
                self._parse_sntp(values, objs.setdefault("sntp", {}))
            elif section == "transaction":
                transaction = objs.setdefault("transaction", {})
                self._copy_token_value(values, "log-full-action", transaction, "log_full_action")
            elif section == "max-lt-link-speed":
                self._copy_token_value(values, "link-speed", objs, "max_lt_link_speed")
            elif section == "security":
                if "welcome-banner" in values:
                    index = values.index("welcome-banner") + 1
                    objs.setdefault("security", {})["welcome_banner"] = " ".join(values[index:])
            elif section in ("loop-id-syntax", "relay-id-syntax"):
                target = objs.setdefault(
                    "loop_id_syntax" if section == "loop-id-syntax" else "relay_id_syntax", {}
                )
                for token, value in zip(values[::2], values[1::2]):
                    target[token.replace("-", "_")] = value
            elif section == "syslog":
                self._parse_syslog(values, objs.setdefault("syslog", {}))

        return objs

    def _copy_token_value(self, tokens, token, target, key, caster=None):
        if token not in tokens:
            return
        index = tokens.index(token) + 1
        if index >= len(tokens):
            return
        value = tokens[index]
        if caster:
            try:
                value = caster(value)
            except (TypeError, ValueError):
                return
        target[key] = value

    def _parse_sntp(self, values, sntp):
        self._copy_token_value(values, "server-ip-addr", sntp, "server_ip_addr")
        self._copy_token_value(values, "polling-rate", sntp, "polling_rate", int)
        self._copy_token_value(values, "timezone-offset", sntp, "timezone_offset", int)
        if "enable" in values:
            sntp["enabled"] = True
        if values[:1] == ["server-table"]:
            entry = {}
            self._copy_token_value(values, "ip-address", entry, "ip_address")
            self._copy_token_value(values, "priority", entry, "priority", int)
            if entry.get("ip_address"):
                sntp.setdefault("servers", []).append(entry)

    def _parse_syslog(self, values, syslog):
        if values[:1] == ["destination"] and len(values) >= 2:
            entry = {"name": values[1]}
            self._copy_token_value(values, "type", entry, "type")
            syslog.setdefault("destinations", []).append(entry)
        elif values[:1] == ["route"] and len(values) >= 2:
            entry = {"destination": values[1]}
            self._copy_token_value(values, "msg-type", entry, "msg_type")
            self._copy_token_value(values, "facility", entry, "facility")
            if "facility" in values:
                start = values.index("facility") + 2
                entry["severities"] = values[start:]
            syslog.setdefault("routes", []).append(entry)

    @staticmethod
    def _split_packed_syntax(line):
        """Split packed loop/relay syntax lines while preserving quoted values."""
        try:
            tokens = shlex.split(line)
        except ValueError:
            return [line]
        if len(tokens) < 5 or tokens[2] not in ("loop-id-syntax", "relay-id-syntax"):
            return [line]
        prefix = " ".join(tokens[:3])
        return [
            '{} {} "{}"'.format(prefix, token, value)
            for token, value in zip(tokens[3::2], tokens[4::2])
        ]
