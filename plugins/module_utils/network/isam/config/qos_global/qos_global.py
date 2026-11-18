# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_global import (
    ATTR_NAMES,
    DEFAULTS,
    LIST_NODES,
    SECTIONS,
    Qos_globalTemplate,
    normalize_line_card,
)


class Qos_global(IsamResourceModule):
    """The isam_qos_global config class.

    Settings are set/reset in place (``no X`` restores the default); one packed
    command per section or line card. ctrl-pkt-policer entries are created per
    protocol and removed with ``configure qos no ctrl-pkt-policer <protocol>``.
    """

    def __init__(self, module):
        super(Qos_global, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="qos_global",
            tmplt=Qos_globalTemplate(),
        )

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    # ----- helpers ---------------------------------------------------------------------
    @staticmethod
    def _index(section, items):
        key = LIST_NODES[section][1]
        result = {}
        for item in items or []:
            if item.get(key) in (None, ""):
                continue
            ident = normalize_line_card(item[key]) if section == "line_cards" else str(item[key])
            result[ident] = dict(item, **{key: ident})
        return result

    @staticmethod
    def _tokens(section, want, have, reset_unwanted):
        """Tokens turning have into want; reset_unwanted also resets attributes want omits."""
        tokens = []
        defaults = DEFAULTS[section]
        for attr in ATTR_NAMES[section]:
            wv = want.get(attr)
            hv = have.get(attr, defaults[attr])
            if wv is not None:
                if wv != hv:
                    tokens.append(Qos_globalTemplate.token(section, attr, wv))
            elif reset_unwanted and hv != defaults[attr]:
                tokens.append(Qos_globalTemplate.token(section, attr, None))
        return tokens

    def _emit(self, section, tokens, identity=None):
        cmd = Qos_globalTemplate.command(section, tokens, identity)
        if cmd and (tokens or section == "ctrl_pkt_policer"):
            self.commands.append(cmd)

    def _named_sections(self):
        """Sections present in the module's config, empty dicts/lists included."""
        config = self._module.params.get("config") or {}
        return [section for section in SECTIONS if config.get(section) is not None]

    # ----- per section -----------------------------------------------------------------
    def _settings(self, section, want, have, reset_unwanted):
        self._emit(section, self._tokens(section, want or {}, have or {}, reset_unwanted))

    def _reset_settings(self, section, have):
        self._emit(section, self._tokens(section, {}, have or {}, True))

    def _list(self, section, want, have, reset_unwanted, drop_unnamed):
        wantd = self._index(section, want)
        haved = self._index(section, have)
        if drop_unnamed:
            for ident in sorted(haved):
                if ident not in wantd:
                    self._remove_entry(section, ident, haved[ident])
        for ident in sorted(wantd):
            entry = wantd[ident]
            have_entry = haved.get(ident)
            tokens = self._tokens(section, entry, have_entry or {}, reset_unwanted)
            if section == "ctrl_pkt_policer":
                if have_entry is None or tokens:
                    self._emit(section, tokens, ident)
            elif tokens:
                self._emit(section, tokens, ident)

    def _remove_entry(self, section, ident, have_entry):
        if section == "ctrl_pkt_policer":
            self.commands.append(Qos_globalTemplate.remove_ctrl_pkt_policer(ident))
        else:
            self._emit(section, self._tokens(section, {}, have_entry, True), ident)

    # ----- states ----------------------------------------------------------------------
    def generate_commands(self):
        want = self.want or {}
        have = self.have or {}

        if self.state == "deleted":
            named = self._named_sections()
            for section in SECTIONS:
                if named and section not in named:
                    continue
                if section in LIST_NODES:
                    haved = self._index(section, have.get(section))
                    wantd = self._index(section, want.get(section))
                    for ident in sorted(haved):
                        if wantd and ident not in wantd:
                            continue
                        self._remove_entry(section, ident, haved[ident])
                else:
                    self._reset_settings(section, have.get(section))
            return

        for section in SECTIONS:
            in_want = section in want
            if self.state == "overridden" and not in_want:
                if section in LIST_NODES:
                    for ident, entry in sorted(self._index(section, have.get(section)).items()):
                        self._remove_entry(section, ident, entry)
                else:
                    self._reset_settings(section, have.get(section))
                continue
            if not in_want:
                continue
            reset = self.state in ("replaced", "overridden")
            if section in LIST_NODES:
                self._list(section, want.get(section), have.get(section), reset, self.state == "overridden")
            else:
                self._settings(section, want.get(section), have.get(section), reset)
