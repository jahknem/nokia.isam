# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    covers_entry,
    requested_sections,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.software_mngt import (
    SOFTWARE_MNGT_NODES,
    Software_mngtTemplate,
    creation_command,
    diff_commands,
    removal_command,
    without_defaults,
)


class Software_mngt(IsamResourceModule):
    """The isam_software_mngt config class (global settings). One grammar table drives
    parsing, rendering and defaults; packed attributes share a line, solo/scalar attributes
    each get their own command."""

    def __init__(self, module):
        super(Software_mngt, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="software_mngt",
            tmplt=Software_mngtTemplate(),
        )

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        # want stays raw: an explicit default value means "reset to default"; have holds
        # non-defaults only (facts strip defaults), so the diff treats defaults as unset
        want = self.want or {}
        have = without_defaults(self.have)
        requested = requested_sections(self._module) if self.state in ("replaced", "deleted") else set()
        for node in SOFTWARE_MNGT_NODES:
            if requested and node["key"] not in requested:
                continue
            if node["is_list"]:
                self._compare_keyed(node, want.get(node["key"]) or [], have.get(node["key"]) or [])
            else:
                self._compare_flat(node, want.get(node["key"]) or {}, have.get(node["key"]) or {})

    def _compare_keyed(self, node, want, have):
        ident = node["identity"]
        wantd = dict((str(e[ident]), e) for e in want)
        haved = dict((str(e[ident]), e) for e in have)

        if self.state == "deleted":
            for name, have_entry in haved.items():
                if wantd and name not in wantd:
                    continue
                want_entry = wantd.get(name) or {}
                if covers_entry(want_entry, have_entry, [ident]):
                    self.commands.append(removal_command(node, name))
                else:
                    named = set(k for k, v in want_entry.items() if k != ident and v is not None)
                    keep = dict((k, v) for k, v in have_entry.items() if k not in named)
                    self.commands.extend(diff_commands(node, name, keep, have_entry, "replaced"))
            return

        if self.state in ("replaced", "overridden"):
            for name in haved:
                if name not in wantd:
                    self.commands.append(removal_command(node, name))

        for name, want_entry in wantd.items():
            have_entry = haved.get(name, {})
            creating = not have_entry and self.state != "rendered"
            before = len(self.commands)
            self.commands.extend(diff_commands(node, name, want_entry, have_entry, self.state))
            if len(self.commands) == before and (self.state == "rendered" or creating):
                # an instance with only a name is created by its bare line
                self.commands.append(creation_command(node, name))

    def _compare_flat(self, node, want, have):
        if self.state == "deleted":
            named = set(k for k, v in want.items() if v is not None)
            keep = dict((k, v) for k, v in have.items() if named and k not in named)
            self.commands.extend(diff_commands(node, None, keep, have, "replaced"))
            return
        self.commands.extend(diff_commands(node, None, want, have, self.state))
