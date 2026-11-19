# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import shlex

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    parse_cli_key_values,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.system.system import (
    Isam_systemArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.system import (
    SETTINGS,
    SETTINGS_LISTS,
    SETTINGS_NODES,
    SYSLOG_SEVERITIES,
    Isam_systemTemplate,
    parse_settings,
    parse_sync_if_timing,
)

# 'configure system security ...' belongs to isam_system_security (the shared-snapshot
# read excludes it from 'system' too); isam_system's own read ignores it as well.
SECURITY_PREFIX = "configure system security"


class Isam_systemFacts(object):
    """The isam system facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Isam_systemArgs.argument_spec

    def get_config(self, connection):
        """The whole resource, or only the instances named in config (targeted gathering)."""
        return get_targeted_config(self._module, connection, "system", "info configure system flat", {
            "sntp.servers": "info configure system sntp server-table ip-address %s flat",
            "syslog.destinations": "info configure system syslog destination %s flat",
            "syslog.routes": "info configure system syslog route %s flat",
            "sync_if_timing.ssm": "info configure system sync-if-timing ssm %s flat",
            "sync_if_timing.synce": "info configure system sync-if-timing synce %s flat",
            "sync_if_timing.ssmout_synce": "info configure system sync-if-timing ssmout-synce %s flat",
        })

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)
        data = unwrap_response(data)

        lines = self._flatten_config(data)
        parser = Isam_systemTemplate(lines=lines, module=self._module)
        parsed = parser.parse()
        objs = self._parse_flat_config(lines)
        for section in ("id", "sntp", "syslog", "sync_if_timing", "transaction"):
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
                if stripped == SECURITY_PREFIX or stripped.startswith(SECURITY_PREFIX + " "):
                    continue
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
            if stripped in ("id", "security", "sntp", "sync-if-timing", "syslog", "transaction", "max-lt-link-speed",
                            "loop-id-syntax", "relay-id-syntax") + tuple(SETTINGS_NODES):
                current_section = stripped
                continue
            if current_section == "security" or (not current_section and stripped.split()[:1] == ["security"]):
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
                # 'configure system id <node-id> name ...'; the legacy block form
                # ('id' / 'name X') has no node id
                if values[0] not in ("name", "location", "contact", "no") + SETTINGS["id"][2] + tuple(
                        attr.cli for attr in SETTINGS["id"][1]):
                    id_section["node_id"] = values[0]
                self._copy_token_value(values, "name", id_section, "name")
                self._copy_token_value(values, "location", id_section, "location")
                self._copy_token_value(values, "contact-person", id_section, "contact")
                self._copy_token_value(values, "nt-intercon-vlan", id_section, "nt_intercon_vlan", int)
                self._copy_token_value(values, "internal-nw-vlan", id_section, "internal_nw_vlan", int)
                self._copy_token_value(values, "system-mac", id_section, "system_mac")
                parse_settings(values[1:], SETTINGS["id"][1], id_section, SETTINGS["id"][2])
            elif section == "sntp":
                self._parse_sntp(values, objs.setdefault("sntp", {}))
            elif section == "transaction":
                transaction = objs.setdefault("transaction", {})
                self._copy_token_value(values, "log-full-action", transaction, "log_full_action")
                parse_settings(values, SETTINGS["transaction"][1], transaction, SETTINGS["transaction"][2])
            elif section in SETTINGS_NODES:
                key = SETTINGS_NODES[section]
                parse_settings(values, SETTINGS[key][1], objs.setdefault(key, {}), SETTINGS[key][2])
            elif section == "max-lt-link-speed":
                self._copy_token_value(values, "link-speed", objs, "max_lt_link_speed")
            elif section in ("loop-id-syntax", "relay-id-syntax"):
                target = objs.setdefault(
                    "loop_id_syntax" if section == "loop-id-syntax" else "relay_id_syntax", {}
                )
                target.update(parse_cli_key_values(values))
            elif section == "syslog":
                self._parse_syslog(values, objs.setdefault("syslog", {}))
            elif section == "sync-if-timing":
                parse_sync_if_timing(values, objs.setdefault("sync_if_timing", {}))

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
        if "enable" in values and values[values.index("enable") - 1:values.index("enable")] != ["no"]:
            sntp["enabled"] = True
        if values[:1] != ["server-table"]:
            parse_settings(values, SETTINGS["sntp"][1], sntp, SETTINGS["sntp"][2])
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
            _node, _ident, attrs, other = SETTINGS_LISTS[("syslog", "destinations")]
            parse_settings(values[2:], attrs, entry, other)
            syslog.setdefault("destinations", []).append(entry)
        elif values[:1] == ["route"] and len(values) >= 2:
            entry = {"destination": values[1]}
            self._copy_token_value(values, "msg-type", entry, "msg_type")
            self._copy_token_value(values, "facility", entry, "facility")
            if "facility" in values:
                # enabled severities only ('no <severity>' is not enabled)
                rest = values[values.index("facility") + 2:]
                entry["severities"] = [
                    token for index, token in enumerate(rest)
                    if token in SYSLOG_SEVERITIES and (index == 0 or rest[index - 1] != "no")
                ]
            _node, _ident, attrs, other = SETTINGS_LISTS[("syslog", "routes")]
            parse_settings(values[2:], attrs, entry, other)
            syslog.setdefault("routes", []).append(entry)
        else:
            parse_settings(values, SETTINGS["syslog"][1], syslog, SETTINGS["syslog"][2])

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
