# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

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
    LISTS,
    SECRET_FIELDS,
    SETTINGS,
    Isam_system_securityTemplate,
    scalar_fields,
    sub_dicts,
)

_MISSING = object()


def _get(config, section, default=None):
    value = config or {}
    for part in section.split("."):
        if not isinstance(value, dict) or part not in value:
            return default
        value = value[part]
    return value


def _settings_part(section, value):
    """Only the attributes a settings node itself carries (no nested lists/blocks)."""
    if not isinstance(value, dict):
        return {}
    keys = set(scalar_fields(section))
    if section == "default_profile":
        keys.add("permissions")
    return dict((k, v) for k, v in value.items() if k in keys and v is not None)


def _named(key, wanted):
    """Whether an instance key is named by a want key; unset trailing identity fields
    (SNMP view subtree, community host-address) match any value."""
    for want_key in wanted:
        if all(w is None or w == h for w, h in zip(want_key, key)):
            return True
    return False


def _diff(want, have):
    """Attributes of want that differ from have (recursing into dicts)."""
    out = {}
    for key, value in want.items():
        if value is None:
            continue
        current = have.get(key)
        if isinstance(value, dict):
            sub = _diff(value, current if isinstance(current, dict) else {})
            if sub:
                out[key] = sub
        elif current != value:
            out[key] = value
    return out


def _absent(want, have):
    """Attributes of have that want does not set (recursing into dicts)."""
    out = {}
    for key, value in have.items():
        if value is None:
            continue
        wanted = want.get(key, _MISSING)
        if isinstance(value, dict):
            sub = _absent(wanted if isinstance(wanted, dict) else {}, value)
            if sub:
                out[key] = sub
        elif wanted is _MISSING or wanted is None:
            out[key] = value
    return out


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

    @staticmethod
    def _index(section, entries):
        ident = LISTS[section][0]
        out = {}
        for entry in entries or []:
            key = tuple(entry.get(f) for f in ident)
            if key[0] is not None:
                out[key] = entry
        return out

    @staticmethod
    def _clean_secrets(section, want, have):
        for field in SECRET_FIELDS.get(section, ()):
            if is_masked_secret(want.get(field)):
                want = dict(want, **{field: have.get(field)})
        return want

    def _targets(self, want, section):
        """Whether 'deleted' acts on a section: all sections without config, else the named ones."""
        return not want or _get(want, section, _MISSING) is not _MISSING

    def generate_commands(self):
        want = self.want or {}
        have = self.have or {}
        for section in LISTS:
            self._list_commands(section, want, have)
        for section in SETTINGS:
            self._settings_commands(section, want, have)

    def _remove(self, section, entry):
        tmplt = Isam_system_securityTemplate
        if LISTS[section][1] == "create":
            self.commands.append(tmplt.render_remove(section, entry))
        else:
            self.commands.extend(tmplt.render_reset(section, entry))

    def _list_commands(self, section, want, have):
        tmplt = Isam_system_securityTemplate
        ident = LISTS[section][0]
        kind = LISTS[section][1]
        wantd = self._index(section, _get(want, section))
        haved = self._index(section, _get(have, section))

        if self.state == "deleted":
            if not self._targets(want, section):
                return
            for key, entry in haved.items():
                if not wantd or _named(key, wantd):
                    self._remove(section, entry)
            return

        if self.state == "overridden":
            for key, entry in haved.items():
                if not _named(key, wantd):
                    self._remove(section, entry)

        for key, entry in wantd.items():
            current = haved.get(key, {})
            entry = self._clean_secrets(section, entry, current)
            changed = _diff(entry, current)
            identity = dict((f, entry.get(f)) for f in ident)
            if changed:
                if kind == "create":
                    self.commands.extend(tmplt.render_entry(section, entry))
                else:
                    changed.update(identity)
                    self.commands.extend(tmplt.render_entry(section, changed))
            if self.state in ("replaced", "overridden") and current:
                stale = _absent(entry, current)
                for field in ident:
                    stale.pop(field, None)
                if stale:
                    stale.update(identity)
                    self.commands.extend(tmplt.render_reset(section, stale))

    def _settings_commands(self, section, want, have):
        tmplt = Isam_system_securityTemplate
        wantd = _settings_part(section, _get(want, section))
        haved = _settings_part(section, _get(have, section))
        if self.state == "deleted":
            # a block holding instance lists (filetransfer, pae) is only reset when
            # config gives one of its own attributes, not for its lists alone
            if (not want or wantd) and haved:
                self.commands.extend(tmplt.render_reset(section, haved))
            return
        if not wantd:
            return
        changed = _diff(wantd, haved)
        if changed:
            self.commands.extend(tmplt.render_entry(section, changed))
        if self.state in ("replaced", "overridden"):
            stale = _absent(wantd, haved)
            if stale:
                self.commands.extend(tmplt.render_reset(section, stale))
