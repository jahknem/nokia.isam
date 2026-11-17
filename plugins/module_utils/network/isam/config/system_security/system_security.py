# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    is_masked_secret,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.system_security import (
    Isam_system_securityTemplate,
)

_LIST_SECTIONS = (
    "operators", "profiles", "snmp_communities", "snmp_views", "snmp_managers",
    "snmp_notify_profiles", "radius_auth_servers", "radius_policies", "radius_dyn_auth_clients",
)
_SECRET_FIELDS = {"operators": ("password",), "radius_auth_servers": ("secret",), "radius_dyn_auth_clients": ("secret",)}


class Isam_system_security(ResourceModule):
    """The isam_system_security config class."""

    def __init__(self, module):
        super(Isam_system_security, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="isam_system_security",
            tmplt=Isam_system_securityTemplate(),
        )

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def _index(self, entries):
        return {e["name"]: e for e in entries or [] if e.get("name") is not None}

    def _clean_secrets(self, section, want, have):
        for field in _SECRET_FIELDS.get(section, ()):
            if is_masked_secret(want.get(field)):
                want = dict(want, **{field: have.get(field)})
        return want

    def _unchanged(self, want, have):
        return all(have.get(k) == v for k, v in want.items() if k != "name")

    def generate_commands(self):
        want = self.want or {}
        have = self.have or {}

        for section in _LIST_SECTIONS:
            wantd = self._index(want.get(section))
            haved = self._index(have.get(section))

            if self.state == "deleted":
                for name in haved:
                    if not wantd or name in wantd:
                        self.commands.append(Isam_system_securityTemplate.render_remove(section, name))
                continue

            if self.state == "overridden":
                for name in haved:
                    if name not in wantd:
                        self.commands.append(Isam_system_securityTemplate.render_remove(section, name))

            for name, entry in iteritems(wantd):
                entry = self._clean_secrets(section, entry, haved.get(name, {}))
                if self.state == "merged" and self._unchanged(entry, haved.get(name, {})):
                    continue
                self.commands.extend(Isam_system_securityTemplate.render_entry(section, entry))

        # settings singleton
        section = "radius_auth_super_user"
        wantd = want.get(section) or {}
        haved = have.get(section) or {}
        if self.state == "deleted":
            if haved:
                self.commands.extend(Isam_system_securityTemplate.render_entry(section, {}))
        elif wantd and not self._unchanged(wantd, haved):
            self.commands.extend(Isam_system_securityTemplate.render_entry(section, wantd))
