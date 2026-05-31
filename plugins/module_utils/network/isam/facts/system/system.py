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
        return connection.get("info configure system")

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)
        if type(data) == tuple:
            data = data[0]

        data = self._flatten_config(data)
        parser = Isam_systemTemplate(lines=data, module=self._module)
        parsed = parser.parse()

        objs = {
            "id": parsed.get("id", {}),
            "security": parsed.get("security", {}),
            "sntp": parsed.get("sntp", {}),
            "syslog": parsed.get("syslog", {}),
            "sync_if_timing": parsed.get("sync_if_timing", {}),
            "transaction": parsed.get("transaction", {}),
        }

        for key in ("port", "poll_interval"):
            if objs.get("sntp", {}).get(key) is not None:
                objs["sntp"][key] = int(objs["sntp"][key])

        if objs.get("transaction", {}).get("timeout") is not None:
            objs["transaction"]["timeout"] = int(objs["transaction"]["timeout"])

        ansible_facts["ansible_network_resources"].pop("system", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )
        facts["system"] = params.get("config", {})
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    def _flatten_config(self, config):
        flat_config = []
        if not config:
            return flat_config

        current = None
        in_system = False

        multi_line_resources = ("id", "security", "sntp", "sync-if-timing", "syslog", "transaction")
        resource_keywords = (
            "id",
            "security",
            "sntp",
            "sync-if-timing",
            "syslog",
            "transaction",
        )

        for raw_line in config.splitlines():
            line = raw_line.split("#", 1)[0].rstrip()
            stripped = line.strip()
            if not stripped or stripped.startswith("echo") or stripped.startswith("#"):
                continue

            if line.startswith("configure system "):
                flat_config.append(line)
                continue

            if stripped == "system":
                in_system = True
                current = None
                continue
            if stripped == "exit":
                current = None
                continue
            if not in_system:
                continue

            if line == stripped:
                matched_kw = None
                for kw in resource_keywords:
                    if stripped == kw or stripped.startswith(kw + " "):
                        matched_kw = kw
                        break

                if matched_kw is not None:
                    if matched_kw not in multi_line_resources:
                        flat_config.append("configure system " + stripped)
                        current = None
                    else:
                        current = "configure system " + stripped
                continue

            if current and stripped:
                flat_config.append(current + " " + stripped)

        return flat_config
