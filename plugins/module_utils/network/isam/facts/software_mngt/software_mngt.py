# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.software_mngt.software_mngt import (
    Software_mngtArgs,
)


class Software_mngtFacts(object):
    """The isam software_mngt facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Software_mngtArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = connection.get("info configure software-mngt flat")
        data = unwrap_response(data)

        software_mngt_config = self._parse_software_mngt_config(data)

        ansible_facts["ansible_network_resources"].pop("software_mngt", None)
        params = utils.remove_empties(
            software_mngt_config
        ) or {}
        facts["software_mngt"] = params
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    def _parse_software_mngt_config(self, config):
        software_mngt = {"database": {}, "oswp": [], "sw_replacement_mode": {}}
        section = None

        for raw_line in config.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith("echo "):
                continue

            if line.startswith("configure software-mngt "):
                self._parse_flat_line(line[len("configure software-mngt "):], software_mngt)
                continue

            if line == "database":
                section = "database"
                continue
            if line == "oswp":
                section = "oswp"
                continue
            if line == "sw-replacement-mode":
                section = "sw_replacement_mode"
                continue
            if line == "exit":
                section = None
                continue

            if section == "database":
                self._parse_database_option(line, software_mngt["database"])
            elif section == "oswp":
                self._parse_oswp_option(line, software_mngt["oswp"])
            elif section == "sw_replacement_mode":
                self._parse_sw_replacement_mode_option(line, software_mngt["sw_replacement_mode"])

        return software_mngt

    def _parse_database_option(self, line, database):
        if line.startswith("version "):
            database["version"] = line.split(None, 1)[1]
        elif line.startswith("url "):
            database["url"] = line.split(None, 1)[1]

    def _parse_oswp_option(self, line, oswp):
        if line == "admin-state":
            oswp.append({"admin_state": True})
        elif line == "no admin-state":
            oswp.append({"admin_state": False})

    def _parse_sw_replacement_mode_option(self, line, sw_rm):
        if line.startswith("mode "):
            sw_rm["mode"] = line.split(None, 1)[1]

    def _parse_flat_line(self, line, software_mngt):
        parts = line.split()
        if not parts:
            return
        if parts[0] == "sw-replacement-mode" and len(parts) > 1:
            software_mngt["sw_replacement_mode"]["mode"] = parts[1]
        elif parts[0] == "oswp" and len(parts) > 1:
            entry = {"id": parts[1]}
            self._copy_token_value(parts, "primary-file-server-id", entry, "primary_file_server_id")
            self._copy_token_value(parts, "second-file-server-id", entry, "second_file_server_id")
            entry["activate"] = "activate" in parts and "no" not in parts[max(parts.index("activate") - 1, 0):parts.index("activate")]
            entry["auto_verify"] = "auto-verify" in parts and "no" not in parts[max(parts.index("auto-verify") - 1, 0):parts.index("auto-verify")]
            software_mngt["oswp"].append(entry)
        elif parts[0] == "database":
            database = software_mngt["database"]
            if "backup" in parts:
                self._copy_token_value(parts, "backup", database, "backup")
            if "backupv6" in parts:
                self._copy_token_value(parts, "backupv6", database, "backupv6")
            if "auto-backup-intvl" in parts:
                self._copy_token_value(parts, "auto-backup-intvl", database, "auto_backup_interval")

    def _copy_token_value(self, parts, token, target, key):
        if token in parts:
            index = parts.index(token) + 1
            if index < len(parts):
                target[key] = parts[index]
