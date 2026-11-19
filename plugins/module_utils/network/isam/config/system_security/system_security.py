# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    changed_values,
    is_masked_secret,
    omitted_values,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.system_security import (
    LISTS,
    NESTED,
    SECRET_FIELDS,
    SETTINGS,
    VIEW_SECTIONS,
    Isam_system_securityTemplate,
    canonical_subtree,
    normalize_policy,
    register_embedded_secrets,
    scalar_fields,
    split_snmp_version,
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


def _split_nested(section, entry):
    """(entry without its nested instance lists, {nested key: list or None})."""
    keys = [kw.replace("-", "_") for kw in NESTED.get(section, {})]
    if not keys or not isinstance(entry, dict):
        return entry, {}
    return (dict((k, v) for k, v in entry.items() if k not in keys),
            dict((k, entry.get(k)) for k in keys))


def _identity_value(section, field, value):
    """An identity value as compared: SNMP view subtrees by the name the device prints."""
    if section in VIEW_SECTIONS and field == "subtree":
        return canonical_subtree(value)
    return value


def _named(key, wanted):
    """Whether an instance key is named by a want key; unset trailing identity fields
    (SNMP view subtree, community host-address) match any value."""
    for want_key in wanted:
        if all(w is None or w == h for w, h in zip(want_key, key)):
            return True
    return False


def _masked_identity(section, entry):
    # '*' is a real SNMP subtree identity (the whole view), not a hidden secret.
    return any(is_masked_secret(entry.get(field)) and not
               (section in VIEW_SECTIONS and field == "subtree" and entry[field] == "*")
               for field in LISTS[section][0])


class Isam_system_security(IsamResourceModule):
    """The isam_system_security config class."""

    def __init__(self, module):
        # Targeted gathering must not issue a read addressed to a redacted name.
        # Other states gather the whole resource and validate before reconciling.
        if module.params.get("state") == "gathered":
            self._check_target_identities(module)
        super(Isam_system_security, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="isam_system_security",
            tmplt=Isam_system_securityTemplate(),
        )
        register_embedded_secrets(module, self.want)

    @staticmethod
    def _index(section, entries):
        ident = LISTS[section][0]
        out = {}
        for entry in entries or []:
            key = tuple(_identity_value(section, f, entry.get(f)) for f in ident)
            if key[0] is not None:
                out[key] = entry
        return out

    @staticmethod
    def _check_target_identities(module):
        for section in LISTS:
            for entry in _get(module.params.get("config"), section) or []:
                if _masked_identity(section, entry):
                    module.fail_json(msg="%s: targeted gathering requires a concrete identity, not a redacted value." % section)

    def _visible_entries(self, section, entries):
        """Never guess the object behind a redacted identity (e.g. SNMP community).

        merged/replaced can safely leave these opaque entries unchanged, with an
        explicit warning. rendered and destructive states must fail closed: ignoring
        them in overridden could remove objects the request intended to retain.
        """
        visible = []
        for entry in entries or []:
            if _masked_identity(section, entry):
                if self.state not in ("merged", "replaced"):
                    self._module.fail_json(msg="%s: %s requires concrete identities, not redacted values."
                                           % (section, self.state))
                self._module.warn("%s: entry with redacted identity left unchanged; supply its concrete identity to manage it."
                                  % section)
            else:
                visible.append(entry)
        return visible

    def _clean_secrets(self, section, want, have):
        """(comparison entry, fields to omit from commands) for redacted credentials."""
        protected = set()
        for field in SECRET_FIELDS.get(section, ()):
            if is_masked_secret(want.get(field)):
                if not have:
                    self._module.fail_json(msg="%s: a redacted %s cannot be used to create or render an entry."
                                           % (section, field))
                want = dict(want, **{field: have.get(field)})
                protected.add(field)
        if section == "snmp_notify_profiles":
            parts = split_snmp_version(want.get("snmp_version"))
            if parts and is_masked_secret(parts[1]):
                current = split_snmp_version(have.get("snmp_version"))
                if not current or current[0] != parts[0]:
                    self._module.fail_json(msg="snmp_notify_profiles: supply a concrete community to create or change snmp_version.")
                want = dict(want, snmp_version=have["snmp_version"])
                protected.add("snmp_version")
        return want, protected

    def _targets(self, want, section):
        """Whether 'deleted' acts on a section: all sections without config, else the named ones."""
        return not want or _get(want, section, _MISSING) is not _MISSING

    def generate_commands(self):
        want = self.want or {}
        have = self.have or {}
        # Validate all identities before any reconciliation (especially overridden).
        self._wanted_entries = {section: self._visible_entries(section, _get(want, section)) for section in LISTS}
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
        wantd = self._index(section, self._wanted_entries[section])
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
            if section in VIEW_SECTIONS and current:
                # same subtree, written as OID vs. the name the device prints
                entry = dict(entry, subtree=current.get("subtree"))
            entry, protected = self._clean_secrets(section, entry, current)
            if section == "radius_policies":
                entry = normalize_policy(entry)
            entry, nested_want = _split_nested(section, entry)
            current, nested_have = _split_nested(section, current)
            changed = changed_values(entry, current)
            identity = dict((f, entry.get(f)) for f in ident)
            nested_changed, nested_remove, nested_reset = self._nested_commands(
                section, identity, nested_want, nested_have)
            self.commands.extend(nested_remove)
            if changed or nested_changed:
                if kind == "create":
                    payload = dict((field, value) for field, value in entry.items()
                                   if field not in protected and not
                                   (field in SECRET_FIELDS.get(section, ()) and is_masked_secret(value)))
                    self.commands.extend(tmplt.render_entry(section, dict(payload, **nested_changed)))
                else:
                    changed.update(identity)
                    changed.update(nested_changed)
                    self.commands.extend(tmplt.render_entry(section, changed))
            self.commands.extend(nested_reset)
            if self.state in ("replaced", "overridden") and current:
                stale = omitted_values(entry, current)
                for field in ident:
                    stale.pop(field, None)
                if stale:
                    stale.update(identity)
                    self.commands.extend(tmplt.render_reset(section, stale))

    def _nested_commands(self, section, identity, nested_want, nested_have):
        """Nested instance lists (radius policy servers) of one list entry.

        Returns (changed nested entries per key, removal commands, reset commands).
        merged only adds/changes the given entries; replaced/overridden also remove
        entries and attributes the want entry does not give.
        """
        tmplt = Isam_system_securityTemplate
        changed, removes, resets = {}, [], []
        replace = self.state in ("replaced", "overridden")
        for kw, id_field in NESTED.get(section, {}).items():
            key = kw.replace("-", "_")
            wanted = nested_want.get(key)
            have = dict((c.get(id_field), c) for c in nested_have.get(key) or [])
            if wanted is None and not replace:
                continue
            wanted = dict((c.get(id_field), c) for c in wanted or [] if c.get(id_field) is not None)
            if replace:
                for index in have:
                    if index not in wanted:
                        removes.append(tmplt.render_nested_remove(section, identity, kw, index))
            out = []
            for index, child in wanted.items():
                current = have.get(index)
                diff = changed_values(child, current or {})
                diff.pop(id_field, None)
                if diff or current is None:
                    diff[id_field] = index
                    out.append(diff)
                if replace and current:
                    stale = omitted_values(child, current)
                    stale.pop(id_field, None)
                    if stale:
                        stale[id_field] = index
                        resets.extend(tmplt.render_nested_reset(section, identity, kw, stale))
            if out:
                changed[key] = out
        return changed, removes, resets

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
        changed = changed_values(wantd, haved)
        if changed:
            self.commands.extend(tmplt.render_entry(section, changed))
        if self.state in ("replaced", "overridden"):
            stale = omitted_values(wantd, haved)
            if stale:
                self.commands.extend(tmplt.render_reset(section, stale))
