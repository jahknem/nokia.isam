# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import dict_merge
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.system import (
    SETTINGS,
    SETTINGS_LISTS,
    render_settings_commands,
    SYNC_LEGACY_FIELDS,
    SYNC_LISTS,
    Isam_systemTemplate,
    render_sync_if_timing,
)


def _legacy_sync(section):
    """Only the sync-if-timing fields compared through PARSERS (mode, source)."""
    if section is None:
        return None
    return dict((k, v) for k, v in section.items() if k in SYNC_LEGACY_FIELDS)


def _sync_values(section):
    """The structured sync-if-timing fields, lists indexed by identity."""
    out = {}
    for key, value in (section or {}).items():
        if key in SYNC_LEGACY_FIELDS or value is None:
            continue
        if key in SYNC_LISTS:
            ident = SYNC_LISTS[key][1]
            out[key] = dict((e[ident], deepcopy(e)) for e in value if e.get(ident) is not None)
        else:
            out[key] = deepcopy(value)
    return out


def _sync_diff(want, have):
    out = {}
    for key, value in want.items():
        if value is None:
            continue
        current = have.get(key)
        if isinstance(value, dict):
            sub = _sync_diff(value, current if isinstance(current, dict) else {})
            if sub:
                out[key] = sub
        elif value != current:
            out[key] = value
    return out


def _sync_absent(want, have):
    out = {}
    for key, value in have.items():
        if value is None:
            continue
        wanted = want.get(key)
        if isinstance(value, dict):
            sub = _sync_absent(wanted if isinstance(wanted, dict) else {}, value)
            if sub:
                out[key] = sub
        elif wanted is None:
            out[key] = value
    return out


def _sync_lists(values):
    """Back from identity-indexed lists to lists, each entry carrying its identity."""
    out = dict(values)
    for key, (_cli, ident) in SYNC_LISTS.items():
        if key in out:
            out[key] = [dict(entry, **{ident: name}) for name, entry in out[key].items()]
    return out


def _settings_kinds(section):
    return dict((option, kind) for option, _cli, kind in SETTINGS[section][1])


def _settings_lists(section):
    return dict((key, (ident, dict((o, k) for o, _c, k in attrs)))
                for (sec, key), (_node, ident, attrs, _other) in SETTINGS_LISTS.items() if sec == section)


def _settings_values(config):
    """{section: {option: value, list: {identity: {option: value}}}} of the SETTINGS attributes.

    Sections absent from config are absent; a False flag is the device default and
    counts as absent on the have side (facts never report it).
    """
    out = {}
    for section in SETTINGS:
        if not isinstance((config or {}).get(section), dict):
            continue
        source = config[section]
        kinds = _settings_kinds(section)
        values = dict((o, source[o]) for o in kinds if source.get(o) is not None)
        for key, (ident, list_kinds) in _settings_lists(section).items():
            entries = {}
            for entry in source.get(key) or []:
                if entry.get(ident) is None:
                    continue
                entries[entry[ident]] = dict((o, entry[o]) for o in list_kinds if entry.get(o) is not None)
            values[key] = entries
        out[section] = values
    return out


def _settings_same(kind, want, have):
    if kind == "bool":
        return bool(want) == bool(have)
    return want == have


def _settings_changed(kinds, want, have):
    return dict((o, v) for o, v in want.items() if o in kinds and not _settings_same(kinds[o], v, have.get(o)))


def _settings_absent(kinds, want, have):
    # have holds non-defaults only; a False flag needs no reset
    return dict((o, v) for o, v in have.items() if o in kinds and want.get(o) is None
                and not (kinds[o] == "bool" and not v))


class Isam_system(ResourceModule):
    """The isam_system config class."""

    def __init__(self, module):
        super(Isam_system, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="system",
            tmplt=Isam_systemTemplate(),
        )
        self.parsers = {
            "id": ["id.name", "id.location", "id.contact"],
            "security": ["security.ssh", "security.telnet", "security.snmp", "security.welcome_banner"],
            "sntp": [
                "sntp.server", "sntp.port", "sntp.poll_interval",
                "sntp.server_ip_addr", "sntp.polling_rate", "sntp.enabled",
                "sntp.timezone_offset",
            ],
            "syslog": ["syslog.server", "syslog.facility", "syslog.severity"],
            "sync_if_timing": ["sync_if_timing.mode", "sync_if_timing.source"],
            "loop_id_syntax": [
                "loop_id_syntax.atm_based_dsl",
                "loop_id_syntax.efm_based_dsl",
                "loop_id_syntax.efm_based_pon",
                "loop_id_syntax.efm_based_epon",
                "loop_id_syntax.efm_based_ngpon2",
            ],
            "relay_id_syntax": [
                "relay_id_syntax.atm_based_dsl",
                "relay_id_syntax.efm_based_dsl",
            ],
            "transaction": ["transaction.timeout"],
            "max_lt_link_speed": ["max_lt_link_speed"],
        }
        self.want = self._normalize_config(self.want)
        self.have = self._normalize_config(self.have)
        self.before = deepcopy(self.have)

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        want = self.want or {}
        have = self.have or {}

        for section, parsers in self.parsers.items():
            if section == "max_lt_link_speed":
                want_section = (
                    {section: want.get(section)} if section in want else None
                )
                have_section = (
                    {section: have.get(section)} if section in have else None
                )
            elif section == "sync_if_timing":
                self._sync_commands(want.get(section), have.get(section))
                want_section = _legacy_sync(want.get(section))
                have_section = _legacy_sync(have.get(section))
            else:
                want_section = want.get(section)
                have_section = have.get(section)

            if self.state == "merged":
                if want_section is not None:
                    want_section = dict_merge(have_section or {}, want_section)

            if self.state == "deleted":
                if want_section is not None:
                    want_section = {}
                else:
                    have_section = {}

            if self.state in ["overridden", "deleted"]:
                if have_section and not want_section:
                    self._compare_section({}, have_section, parsers)

            if want_section is not None:
                self._compare_section(want_section, have_section or {}, parsers)

        self._settings_commands(want, have)

    def _settings_commands(self, want, have):
        """Settings attributes of id/sntp/syslog/transaction and the settings-only nodes
        (external-leds, auto-laser-shutdown, auto-switch, zero-touch-provision, pon-ont,
        nt-sftp), plus the attributes of existing syslog destinations/routes.

        merged sets what differs; replaced/overridden also reset ('no <kw>') what a given
        section (or listed entry) omits, overridden also omitted sections and entries;
        deleted resets the given sections. Syslog destinations/routes are never created
        or removed here, only their attributes are set/reset.
        """
        wantv = _settings_values(want)
        havev = _settings_values(have)
        changed = {}
        reset = {}
        for section in SETTINGS:
            kinds = _settings_kinds(section)
            lists = _settings_lists(section)
            w = wantv.get(section)
            h = havev.get(section) or {}
            if w is None and self.state != "overridden":
                continue
            if self.state == "deleted":
                set_values, reset_values = {}, _settings_absent(kinds, {}, h)
            else:
                w = w or {}
                set_values = _settings_changed(kinds, w, h)
                reset_values = {}
                if self.state in ("replaced", "overridden"):
                    reset_values = _settings_absent(kinds, w, h)
            for key, (ident, list_kinds) in lists.items():
                w_entries = (w or {}).get(key) or {}
                h_entries = h.get(key) or {}
                set_list, reset_list = [], []
                if self.state == "deleted":
                    reset_list = [dict(_settings_absent(list_kinds, {}, e), **{ident: n}) for n, e in h_entries.items()]
                else:
                    for name, entry in w_entries.items():
                        diff = _settings_changed(list_kinds, entry, h_entries.get(name) or {})
                        if diff:
                            set_list.append(dict(diff, **{ident: name}))
                    if self.state in ("replaced", "overridden"):
                        for name, entry in h_entries.items():
                            if name not in w_entries and self.state != "overridden":
                                continue
                            absent = _settings_absent(list_kinds, w_entries.get(name) or {}, entry)
                            if absent:
                                reset_list.append(dict(absent, **{ident: name}))
                set_values.pop(key, None)
                reset_values.pop(key, None)
                if set_list:
                    set_values[key] = set_list
                if reset_list:
                    reset_values[key] = reset_list
            if set_values:
                changed[section] = set_values
            if reset_values:
                reset[section] = reset_values
        node_id = ((want or {}).get("id") or {}).get("node_id") or ((have or {}).get("id") or {}).get("node_id")
        self.commands.extend(render_settings_commands(changed, node_id=node_id))
        self.commands.extend(render_settings_commands(reset, reset=True, node_id=node_id))

    def _sync_commands(self, want_section, have_section):
        """sync-if-timing references, SSM, SyncE and BITS settings (not PARSERS based).

        Lists are fixed instances (timing references, SyncE ports): an instance not
        wanted is reset, never removed.
        """
        if want_section is None and self.state != "overridden":
            return
        wantv = _sync_values(want_section)
        havev = _sync_values(have_section)
        if self.state == "deleted":
            reset = havev
            changed = {}
        else:
            changed = _sync_diff(wantv, havev)
            reset = {}
            if self.state in ("replaced", "overridden"):
                reset = _sync_absent(wantv, havev)
        # list entries keep only the attributes to render; identity is re-added below
        for key, (_cli, ident) in SYNC_LISTS.items():
            for values in (changed, reset):
                for name in list((values.get(key) or {})):
                    entry = values[key][name]
                    entry.pop(ident, None)
                    if not entry:
                        del values[key][name]
        self.commands.extend(render_sync_if_timing(_sync_lists(changed)))
        self.commands.extend(render_sync_if_timing(_sync_lists(reset), reset=True))

    def _compare_section(self, want, have, parsers):
        self.compare(parsers=parsers, want=want, have=have)

    def _normalize_config(self, config):
        return deepcopy(config or {})
