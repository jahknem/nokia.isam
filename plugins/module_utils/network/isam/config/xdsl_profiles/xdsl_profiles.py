# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_profiles import (
    PROFILE_TYPES,
    SCHEMAS,
    Xdsl_profilesTemplate,
)


class Xdsl_profiles(IsamResourceModule):
    """The isam_xdsl_profiles config class."""

    def __init__(self, module):
        self.template = Xdsl_profilesTemplate()
        super(Xdsl_profiles, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="xdsl_profiles",
            tmplt=self.template,
        )

    def execute_module(self):
        # parsed / gathered: the result is self.before, read through Facts like the other modules
        # (gathered: targeted when config names profiles, device errors fail the module).
        if self.state in ("parsed", "gathered"):
            pass
        elif self.state == "rendered":
            self.generate_commands()
        else:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        want = self.template.normalize(self.want or {})
        have = self.template.normalize(self.have or {})

        if self.state == "rendered":
            self.commands = self._render_all(want)
            return

        if self.state == "deleted":
            self.commands = self._delete(want, have)
            return

        if self.state == "overridden":
            self.commands = self._delete_unspecified(want, have)
            self.commands.extend(self._replace_or_merge(want, have, replace=True))
            return

        self.commands = self._replace_or_merge(want, have, replace=self.state == "replaced")

    def _replace_or_merge(self, want, have, replace=False):
        commands = []
        for profile_type in PROFILE_TYPES:
            haved = self._index(have.get(profile_type))
            for profile in want.get(profile_type) or []:
                key = self.template.key_for(profile)
                current = haved.get(key, {})
                if replace:
                    # replaced keeps its behaviour: a differing profile is deleted and rendered in full.
                    if self.template.canonical(profile_type, profile) != self.template.canonical(profile_type, current):
                        if current:
                            commands.append(self.template.delete_profile(profile_type, profile))
                        commands.extend(self.template.render_profile(profile_type, profile, full=True))
                else:
                    commands.extend(self._merge_profile(profile_type, profile, current))
        return commands

    def _merge_profile(self, profile_type, want, have):
        if not have:
            return self.template.render_profile(profile_type, want, full=True)

        commands = []
        profile_id = want.get("id")
        prefix = "configure xdsl %s %s" % (PROFILE_TYPES[profile_type], profile_id)
        if want.get("name") and want.get("name") != have.get("name"):
            commands.append("%s name %s" % (prefix, want.get("name")))

        schema = SCHEMAS[profile_type]
        body = dict((k, v) for k, v in want.items() if k not in ("commands", "active"))
        for line in self.template.diff_lines(schema, body, have):
            commands.append("%s %s" % (prefix, line))
        if want.get("active") is not None and bool(want["active"]) != bool(have.get("active")):
            commands.append("%s %sactive" % (prefix, "" if want["active"] else "no "))

        # Modelled commands were folded into options by normalize(); compare the rest
        # also against the rendered state so a command the facts now model stays idempotent.
        have_commands = set(have.get("commands") or [])
        have_commands.update(self.template.render_lines(schema, have))
        for command in want.get("commands") or []:
            if command not in have_commands:
                commands.append("%s %s" % (prefix, command))
        return commands

    def _delete(self, want, have):
        """Without config: every profile. With config: only the named profiles; profile
        types the config does not name are left alone (lines use them)."""
        commands = []
        requested = any(want.get(profile_type) for profile_type in PROFILE_TYPES)
        for profile_type in PROFILE_TYPES:
            if requested and not want.get(profile_type):
                continue
            haved = self._index(have.get(profile_type))
            targets = want.get(profile_type) if requested else have.get(profile_type) or []
            for profile in targets:
                if not requested or self.template.key_for(profile) in haved:
                    commands.append(self.template.delete_profile(profile_type, profile))
        return commands

    def _delete_unspecified(self, want, have):
        commands = []
        for profile_type in PROFILE_TYPES:
            wantd = self._index(want.get(profile_type))
            for profile in have.get(profile_type) or []:
                if self.template.key_for(profile) not in wantd:
                    commands.append(self.template.delete_profile(profile_type, profile))
        return commands

    def _render_all(self, data):
        commands = []
        for profile_type in PROFILE_TYPES:
            for profile in data.get(profile_type) or []:
                commands.extend(self.template.render_profile(profile_type, profile, full=True))
        return commands

    def _index(self, profiles):
        return dict((self.template.key_for(profile), profile) for profile in profiles or [])
