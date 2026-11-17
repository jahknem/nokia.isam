# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    iter_cli_fields,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.isam_equipment.isam_equipment import (
    Isam_equipmentArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.isam_equipment import (
    Isam_equipmentTemplate,
)


class Isam_equipmentFacts(object):
    """The isam equipment facts class."""

    # Include known detail-only attributes when tokenizing, even though this
    # resource does not model them. Their values must not be mistaken for a
    # supported flag (e.g. a capability profile named "unlock"). The existing
    # NetworkTemplate remains responsible for selecting/validating public fields.
    _BOOL_FIELDS = {"slot": ("unlock", "power-down", "board-40gkr4")}
    _VALUE_FIELDS = {
        "shelf": ("planned-type",),
        "slot": ("planned-type", "alarm-profile", "capab-profile", "operational-mode", "dual-host-ip", "dual-host-loc"),
        "applique": ("planned-type",),
        "protection-group": ("admin-status", "eps-quenchfactor"),
    }

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Isam_equipmentArgs.argument_spec

    def get_config(self, connection):
        """The whole resource, or only the instances named in config (targeted gathering)."""
        return get_targeted_config(self._module, connection, "isam_equipment", "info configure equipment flat", {
            "shelves": "info configure equipment shelf %s flat",
            "slots": "info configure equipment slot %s flat detail",
            "appliques": "info configure equipment applique %s flat",
            "protection_groups": "info configure equipment protection-group %s flat",
            "diagnostics_sfp": "info configure equipment diagnostics sfp %s flat",
            "protection_elements": "info configure equipment protection-element %s flat",
            "racks": "info configure equipment rack %s flat",
            "external_link_assigns": "info configure equipment external-link-assign %s flat",
            "external_link_hosts": "info configure equipment external-link-host %s flat",
        })

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)
        data = unwrap_response(data)

        data = self._flatten_config(data)
        parser = Isam_equipmentTemplate(lines=data, module=self._module)
        parsed = parser.parse()

        objs = {
            "shelves": list(parsed.get("shelves", {}).values()),
            "slots": list(parsed.get("slots", {}).values()),
            "appliques": list(parsed.get("appliques", {}).values()),
            "protection_groups": list(parsed.get("protection_groups", {}).values()),
            "diagnostics_sfp": list(parsed.get("diagnostics_sfp", {}).values()),
            "protection_elements": list(parsed.get("protection_elements", {}).values()),
            "racks": list(parsed.get("racks", {}).values()),
            "external_link_assigns": list(parsed.get("external_link_assigns", {}).values()),
            "external_link_hosts": list(parsed.get("external_link_hosts", {}).values()),
            "envbox": parsed.get("envbox", {}),
            "isam": parsed.get("isam", {}),
        }

        for group in objs["protection_groups"]:
            group["id"] = int(group["id"])
            if "eps_quenchfactor" in group:
                group["eps_quenchfactor"] = int(group["eps_quenchfactor"])
        for sfp in objs["diagnostics_sfp"]:
            if "rssi_prof_id" in sfp:
                sfp["rssi_prof_id"] = int(sfp["rssi_prof_id"])

        ansible_facts["ansible_network_resources"].pop("isam_equipment", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )
        facts["isam_equipment"] = params.get("config", {})
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    def _flatten_config(self, config):
        flat_config = []
        if not config:
            return flat_config

        current = None
        in_equipment = False
        resources = ("shelf ", "slot ", "applique ", "protection-group ")
        fields = ("planned-type ", "unlock", "no unlock", "admin-status ", "eps-quenchfactor ")

        for raw_line in config.splitlines():
            line = raw_line.split("#", 1)[0].rstrip()
            stripped = line.strip()
            if not stripped or stripped.startswith("echo") or stripped.startswith("#"):
                continue

            if line.startswith((
                "configure equipment shelf ",
                "configure equipment slot ",
                "configure equipment applique ",
                "configure equipment protection-group ",
            )):
                flat_config.extend(self._split_packed_line(line))
                # A scoped hierarchical dump may start with its complete path.
                if len(line.split()) == 4:
                    in_equipment = True
                    current = line
                continue

            if line.startswith((
                "configure equipment diagnostics sfp ",
                "configure equipment protection-element ",
                "configure equipment rack ",
                "configure equipment external-link-assign ",
                "configure equipment external-link-host ",
                "configure equipment envbox",
                "configure equipment isam",
            )):
                flat_config.extend(self._split_subregion_line(line))
                continue

            if stripped in ("equipment", "configure equipment"):
                in_equipment = True
                current = None
                continue
            if stripped == "exit":
                current = None
                continue
            if stripped.startswith("configure "):
                in_equipment = False
                current = None
                continue
            if not in_equipment:
                continue

            if line == stripped and stripped.startswith(resources):
                current = "configure equipment " + stripped
                continue
            if current and stripped.startswith(fields):
                flat_config.extend(self._split_packed_line(current + " " + stripped))

        return flat_config

    def _split_packed_line(self, line):
        """Expand compact equipment properties into existing template commands."""
        tokens = line.split()
        if len(tokens) < 5:
            return []
        resource = tokens[2]
        prefix = " ".join(tokens[:4])
        commands = []
        for negate, key, value in iter_cli_fields(
            tokens[4:],
            bool_fields=self._BOOL_FIELDS.get(resource, ()),
            value_fields=self._VALUE_FIELDS.get(resource, ()),
        ):
            suffix = ("no " if negate else "") + key
            if value is not None:
                suffix += " " + value
            commands.append(prefix + " " + suffix)
        return commands

    @staticmethod
    def _split_subregion_line(line):
        """Expand the newer equipment sub-regions into one command per attribute."""
        tokens = line.split()
        resource = tokens[2]
        if resource == "diagnostics":  # configure equipment diagnostics sfp <id>
            depth = 5
        elif resource in ("envbox", "isam"):  # no identity
            depth = 3
        else:  # protection-element / rack / external-link-assign / external-link-host <id>
            depth = 4
        prefix = " ".join(tokens[:depth])
        value_fields = ("rssi-prof-id", "rssi-state", "redcy-ctrl-status", "description", "remote", "direction")
        commands = []
        for negate, key, value in iter_cli_fields(tokens[depth:], bool_fields=("enable-supervise",), value_fields=value_fields):
            suffix = ("no " if negate else "") + key
            if value is not None:
                suffix += " " + value
            commands.append(prefix + " " + suffix)
        return commands
