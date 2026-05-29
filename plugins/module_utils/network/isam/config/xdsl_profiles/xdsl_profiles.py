# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.xdsl_profiles.xdsl_profiles import (
    Xdsl_profilesFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_profiles import (
    PROFILE_TYPES,
    Xdsl_profilesTemplate,
)


class Xdsl_profiles(ResourceModule):
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
        if self.state == "parsed":
            self.result["parsed"] = self.template.normalize(
                self.template.parse(self._module.params.get("running_config"))
            )
        elif self.state == "gathered":
            ansible_facts = {"ansible_network_resources": {}}
            facts = Xdsl_profilesFacts(self._module).populate_facts(self._connection, ansible_facts)
            self.result["gathered"] = facts.get("ansible_network_resources", {}).get("xdsl_profiles", {})
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
                    if self._without_empty(profile) != self._without_empty(current):
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

        scalar = dict(want)
        wanted_commands = scalar.pop("commands", []) or []
        scalar.pop("id", None)
        scalar.pop("name", None)
        for key, value in iteritems(scalar):
            if value != have.get(key):
                commands.extend(self.template.render_profile(profile_type, {"id": profile_id, key: value}, full=False))

        have_commands = set(have.get("commands") or [])
        for command in wanted_commands:
            if command not in have_commands:
                commands.append("%s %s" % (prefix, command))
        return commands

    def _delete(self, want, have):
        commands = []
        for profile_type in PROFILE_TYPES:
            targets = want.get(profile_type) or have.get(profile_type) or []
            haved = self._index(have.get(profile_type))
            for profile in targets:
                if not want.get(profile_type) or self.template.key_for(profile) in haved:
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

    def _without_empty(self, profile):
        return dict((k, v) for k, v in (profile or {}).items() if v is not None and v != [] and v != {})
