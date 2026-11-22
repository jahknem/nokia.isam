# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_whole_node_targeted,
    unwrap_response,
)
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
        """The whole vlan node, read once; per-profile outcomes for a targeted request.

        The device has no single-instance read for priority-regen profiles
        ("invalid token"); it only answers the whole 'info configure vlan' node.
        An explicit targeted request (state gathered, config names profiles)
        reads the node once and reports per-profile read_outcomes from the
        parsed catalog (get_whole_node_targeted): present when the catalog
        lists the profile, unknown when it does not. The gathered string stays
        the full catalog, unfiltered.
        """
        return get_whole_node_targeted(
            self._module, connection, "isam_vlan_global", "info configure vlan flat",
            ("priority_regen",), lambda data: self._parse_config(data)[0],
        )

    def _parse_config(self, data):
        """The parsed full catalog: (the vlan dict, its parser)."""
        data = unwrap_response(data)

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
                for key in list(entry.keys()):
                    if entry[key] == "":
                        entry.pop(key)
                for pbit in ("id", "pbit0", "pbit1", "pbit2", "pbit3", "pbit4", "pbit5", "pbit6", "pbit7"):
                    if pbit in entry and entry[pbit] != "":
                        entry[pbit] = int(entry[pbit])
            objs["priority_regen"] = priority_regen

        tpid = parsed.get("tpid", {})
        if tpid:
            objs["tpid"] = tpid

        vmac_address_format = parsed.get("vmac_address_format", {})
        if vmac_address_format:
            if vmac_address_format.get("host_id") == "":
                vmac_address_format.pop("host_id")
            elif "host_id" in vmac_address_format:
                vmac_address_format["host_id"] = int(vmac_address_format["host_id"])
            objs["vmac_address_format"] = vmac_address_format

        return objs, parser

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)

        objs, parser = self._parse_config(data)

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
                if stripped == "configure vlan":
                    in_vlan = True
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

            if in_subsection and stripped.startswith(("drop-unknown-multicast", "no drop-unknown-multicast", "priority-policy", "no priority-policy")):
                flat_config.append("configure vlan broadcast-frames " + stripped)
            elif stripped.startswith(("priority-regen", "no tpid", "no vmac-address-format")):
                flat_config.append("configure vlan " + stripped)
            elif stripped.startswith("tpid"):
                flat_config.append("configure vlan " + stripped)
            elif stripped.startswith("vmac-address-format"):
                flat_config.append("configure vlan " + stripped)

        return flat_config
