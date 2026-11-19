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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.voice_sip import (
    VOICE_SIP_NODES,
    Isam_voice_sipTemplate,
    diff_tokens,
    instance_command,
    is_removable,
    removal_command,
    without_defaults,
)


class Isam_voice_sip(IsamResourceModule):
    """The isam_voice_sip config class (global settings: instances are created/removable,
    flat sections are reset). One grammar table drives parsing, rendering and defaults."""

    def __init__(self, module):
        super(Isam_voice_sip, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="voice_sip",
            tmplt=Isam_voice_sipTemplate(),
        )

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        rendering = self.state == "rendered"
        want = (self.want or {}) if rendering else without_defaults(self.want)
        have = without_defaults(self.have)
        # replaced/deleted with config touch only the named sections; overridden and
        # deleted without config touch every section
        requested = requested_sections(self._module) if self.state in ("replaced", "deleted") else set()

        for node in VOICE_SIP_NODES:
            if requested and node["key"] not in requested:
                continue
            if node["is_list"]:
                self._compare_keyed(node, want.get(node["key"]) or [], have.get(node["key"]) or [])
            else:
                self._compare_flat(node, want.get(node["key"]) or {}, have.get(node["key"]) or {})

    def _compare_keyed(self, node, want, have):
        wantd = dict((e["name"], e) for e in want)
        haved = dict((e["name"], e) for e in have)

        if self.state == "deleted":
            for name, have_entry in haved.items():
                if wantd and name not in wantd:
                    continue
                want_entry = wantd.get(name) or {}
                if covers_entry(want_entry, have_entry, ["name"]):
                    self.commands.append(removal_command(node, name))
                else:
                    self._reset_named(node, name, want_entry, have_entry)
            return

        if self.state in ("replaced", "overridden"):
            for name, have_entry in haved.items():
                if name not in wantd:
                    self.commands.append(removal_command(node, name))

        for name, want_entry in wantd.items():
            have_entry = haved.get(name, {})
            creating = not have_entry and self.state != "rendered"
            if creating:
                self._require_mandatory(node, name, want_entry)
            groups = diff_tokens(node, want_entry, have_entry, self.state)
            for cli_node, tokens in groups.items():
                self.commands.append(instance_command(dict(node, cli=cli_node), name, tokens))
            if not groups and (self.state == "rendered" or creating):
                # an instance with only a name is created by its bare line
                self.commands.append(instance_command(node, name, []))

    def _compare_flat(self, node, want, have):
        if self.state == "deleted":
            named = set(k for k, v in want.items() if v is not None)
            self._reset_flat(node, None, have, named or None)
            return
        for cli_node, tokens in diff_tokens(node, want, have, self.state).items():
            self.commands.append(instance_command(dict(node, cli=cli_node), None, tokens))

    def _reset_named(self, node, name, want_entry, have_entry):
        """deleted naming attributes: reset only those the device currently has."""
        named = set(k for k, v in want_entry.items() if k != "name" and v is not None)
        groups = {}
        for option, cli, kind, _d, _c, sub in node["attrs"]:
            if option in named and have_entry.get(option) is not None and is_removable(kind):
                groups.setdefault(sub or node["cli"], []).extend(["no", cli])
        for cli_node, tokens in groups.items():
            self.commands.append(instance_command(dict(node, cli=cli_node), name, tokens))

    def _reset_flat(self, node, name, have, named):
        """Reset the flat section's set attributes (all when named is None)."""
        groups = {}
        for option, cli, kind, _d, _c, sub in node["attrs"]:
            if (named is None or option in named) and have.get(option) is not None and is_removable(kind):
                groups.setdefault(sub or node["cli"], []).extend(["no", cli])
        for cli_node, tokens in groups.items():
            self.commands.append(instance_command(dict(node, cli=cli_node), name, tokens))

    def _require_mandatory(self, node, name, want_entry):
        missing = [o for o in node["mandatory"] if want_entry.get(o) is None]
        if missing:
            self._module.fail_json(
                msg="Creating %s '%s' requires %s (mandatory at creation, no removal form)."
                % (node["cli"], name, ", ".join(missing))
            )
