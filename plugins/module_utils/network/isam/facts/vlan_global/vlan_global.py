# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.vlan_global.vlan_global import (
    Isam_vlan_globalArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.vlan_global import (
    Isam_vlan_globalTemplate,
)


class Isam_vlan_globalFacts(object):
    """The isam_vlan_global facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Isam_vlan_globalArgs.argument_spec

    def get_config(self, connection):
        return connection.get("info configure vlan")

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)
        if type(data) == tuple:
            data = data[0]

        data = self._flatten_config(data)
        parser = Isam_vlan_globalTemplate(lines=data, module=self._module)
        parsed = parser.parse()

        objs = {}

        broadcast_frames = parsed.get("broadcast_frames", {})
        if broadcast_frames:
            objs["broadcast_frames"] = broadcast_frames

        priority_regen = list(parsed.get("priority_regen", {}).values())
        if priority_regen:
            for entry in priority_regen:
                if "dot1p" in entry:
                    entry["dot1p"] = int(entry["dot1p"])
                if "regen_dot1p" in entry:
                    entry["regen_dot1p"] = int(entry["regen_dot1p"])
            objs["priority_regen"] = priority_regen

        tpid = parsed.get("tpid", {})
        if tpid:
            objs["tpid"] = tpid

        vmac_address_format = parsed.get("vmac_address_format", {})
        if vmac_address_format:
            objs["vmac_address_format"] = vmac_address_format

        ansible_facts["ansible_network_resources"].pop("isam_vlan_global", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )
        facts["isam_vlan_global"] = params.get("config", {})
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    def _flatten_config(self, config):
        flat_config = []
        if not config:
            return flat_config

        in_vlan = False
        in_subsection = False

        for raw_line in config.splitlines():
            line = raw_line.split("#", 1)[0].rstrip()
            stripped = line.strip()
            if not stripped or stripped.startswith("echo") or stripped.startswith("#"):
                continue

            if line.startswith("configure vlan"):
                flat_config.append(line)
                continue

            if stripped == "vlan":
                in_vlan = True
                continue
            if stripped == "exit":
                if in_subsection:
                    in_subsection = False
                else:
                    in_vlan = False
                continue
            if not in_vlan:
                continue

            if stripped == "broadcast-frames":
                in_subsection = True
                continue

            if in_subsection and stripped.startswith("drop-unknown-multicast"):
                flat_config.append("configure vlan broadcast-frames " + stripped)
            elif stripped.startswith("priority-regen"):
                flat_config.append("configure vlan " + stripped)
            elif stripped.startswith("tpid"):
                flat_config.append("configure vlan " + stripped)
            elif stripped.startswith("vmac-address-format"):
                flat_config.append("configure vlan " + stripped)

        return flat_config
