# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from ansible.module_utils._text import to_text
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts import get_resource_connection
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ipv6_antispoofing_slot import Isam_ipv6_antispoofing_slotTemplate


class Isam_ipv6_antispoofing_slotFacts(object):
    def __init__(self, module):
        self._module = module
        self.argument_spec = {}

    def get_config(self, connection):
        """The whole resource, or only the slots named in config (targeted gathering).

        Both read the hierarchical output (no flat), which _flatten_config understands.
        """
        return get_targeted_config(self._module, connection, "isam_ipv6_antispoofing_slot", "info configure ipv6-antispoofing slot", {
            "config": "info configure ipv6-antispoofing slot %s",
        })

    def populate_facts(self, connection, ansible_facts, data=None):
        if data is None:
            data = self.get_config(connection)
        lines = self._flatten_config(unwrap_response(data))
        parsed = Isam_ipv6_antispoofing_slotTemplate(lines=lines, module=self._module).parse()
        ansible_facts["ansible_network_resources"]["isam_ipv6_antispoofing_slot"] = list(parsed.values())
        return ansible_facts

    @staticmethod
    def _flatten_config(config):
        lines = []
        in_resource = False
        slot = None
        for raw_line in (config or "").splitlines():
            stripped = raw_line.split("#", 1)[0].strip()
            if not stripped or stripped.startswith(("echo", "#")):
                continue
            if stripped.startswith("configure ipv6-antispoofing slot "):
                tokens = stripped.split()
                if len(tokens) == 4:
                    # Block of one slot: "configure ipv6-antispoofing slot <slot>", then its attributes.
                    slot = tokens[3]
                else:
                    lines.append(stripped)
                in_resource = False
                continue
            if stripped in ("ipv6-antispoofing", "configure ipv6-antispoofing"):
                in_resource = True
                continue
            if in_resource and stripped.startswith("slot "):
                slot = stripped.split(None, 1)[1]
                in_resource = True
                continue
            if stripped == "exit":
                slot = None
                continue
            if slot and (stripped.startswith("bit-len ") or stripped == "no bit-len"):
                lines.append("configure ipv6-antispoofing slot {0} {1}".format(slot, stripped))
        return lines

    def get_facts(self, legacy_facts_type=None, resource_facts_type=None, data=None):
        facts = {"ansible_network_resources": {}}
        try:
            self.populate_facts(get_resource_connection(self._module), facts, data)
        except Exception as exc:  # like netcommon's facts: a clear failure, no traceback
            self._module.fail_json(msg=to_text(exc))
        return facts, []
