# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.traps import (
    Isam_trapsTemplate,
    TRAP_TYPE_NAMES,
    SHAPING_FIELDS,
)


class Isam_traps(ResourceModule):
    def __init__(self, module):
        super(Isam_traps, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="isam_traps",
            tmplt=Isam_trapsTemplate(),
        )

    def execute_module(self):
        if self.state == "rendered":
            self._render_commands()
        elif self.state not in ["parsed", "gathered"]:
            self._generate_commands()
            self.run_commands()
        return self.result

    def _render_commands(self):
        for entry in (self.want or {}).get("definitions", []):
            self._render_definition(entry)
        for entry in (self.want or {}).get("managers", []):
            self._render_manager(entry)
        for entry in (self.want or {}).get("v6managers", []):
            self._render_v6manager(entry)

    def _render_definition(self, entry):
        name = entry.get("name")
        if not name:
            return
        if "priority" in entry and entry["priority"]:
            self.commands.append(
                "configure trap definition %s priority %s" % (name, entry["priority"])
            )
        else:
            self.commands.append("configure trap definition %s" % name)

    def _render_manager(self, entry):
        address = entry.get("address")
        if not address:
            return
        parts = ["configure trap manager %s" % address]
        if "priority" in entry and entry["priority"]:
            parts.append("priority %s" % entry["priority"])
        for cli_name in TRAP_TYPE_NAMES:
            field = cli_name.replace("-", "_")
            val = entry.get(field)
            if val is True:
                parts.append(cli_name)
            elif val is False:
                parts.append("no %s" % cli_name)
        for field, cli_name in SHAPING_FIELDS:
            val = entry.get(field)
            if val is not None and val != "":
                parts.append("%s %s" % (cli_name, val))
        self.commands.append(" ".join(parts))

    def _render_v6manager(self, entry):
        address = entry.get("ipv6address")
        if not address:
            return
        parts = ["configure trap v6manager %s" % address]
        if "priority" in entry and entry["priority"]:
            parts.append("priority %s" % entry["priority"])
        for cli_name in TRAP_TYPE_NAMES:
            field = cli_name.replace("-", "_")
            val = entry.get(field)
            if val is True:
                parts.append(cli_name)
            elif val is False:
                parts.append("no %s" % cli_name)
        for field, cli_name in SHAPING_FIELDS:
            val = entry.get(field)
            if val is not None and val != "":
                parts.append("%s %s" % (cli_name, val))
        self.commands.append(" ".join(parts))

    def _generate_commands(self):
        want = deepcopy(self.want) or {}
        have = deepcopy(self.have) or {}

        self._compare_section(want.get("definitions", []), have.get("definitions", []),
                              "definitions", "name")
        self._compare_section(want.get("managers", []), have.get("managers", []),
                              "managers", "address",
                              no_prefix="configure trap no manager %s")
        self._compare_section(want.get("v6managers", []), have.get("v6managers", []),
                              "v6managers", "ipv6address",
                              no_prefix="configure trap no v6manager %s")

    def _compare_section(self, want_list, have_list, section, key_field, no_prefix=None):
        w_map = {e[key_field]: e for e in want_list if e.get(key_field)}
        h_map = {e[key_field]: e for e in have_list if e.get(key_field)}

        if self.state == "merged":
            w_map = dict_merge(h_map, w_map)

        if self.state == "deleted":
            if w_map:
                h_map = {k: v for k, v in iteritems(h_map) if k in w_map}
                w_map = {}
            else:
                h_map = dict(h_map)
                w_map = {}

        if self.state in ["overridden", "deleted"]:
            for key, have_entry in iteritems(h_map):
                if key not in w_map:
                    if no_prefix:
                        self.commands.append(no_prefix % key)
                    else:
                        self._remove_entry_fields(have_entry, section, key_field)

        for key, want_entry in iteritems(w_map):
            have_entry = h_map.pop(key, {})
            self._compare_entry(want_entry, have_entry, section, key_field)

    def _remove_entry_fields(self, entry, section, key_field):
        if section == "definitions":
            name = entry.get(key_field)
            if entry.get("priority"):
                self.commands.append(
                    "configure trap definition %s no priority" % name
                )

    def _compare_entry(self, want, have, section, key_field):
        key = want.get(key_field)
        if not key:
            return

        if section == "definitions":
            self._compare_definition_fields(name=key, want=want, have=have)
        elif section == "managers":
            self._compare_manager_fields(address=key, want=want, have=have, prefix="manager", key_field="address")
        elif section == "v6managers":
            self._compare_manager_fields(address=key, want=want, have=have, prefix="v6manager", key_field="ipv6address")

    def _compare_definition_fields(self, name, want, have):
        w_prio = want.get("priority")
        h_prio = have.get("priority")
        if w_prio != h_prio:
            if w_prio:
                self.commands.append(
                    "configure trap definition %s priority %s" % (name, w_prio)
                )
            elif h_prio:
                self.commands.append(
                    "configure trap definition %s no priority" % name
                )

    def _compare_manager_fields(self, address, want, have, prefix, key_field):
        w_prio = want.get("priority")
        h_prio = have.get("priority")
        if w_prio != h_prio:
            if w_prio:
                self.commands.append(
                    "configure trap %s %s priority %s" % (prefix, address, w_prio)
                )
            elif h_prio:
                self.commands.append(
                    "configure trap %s %s no priority" % (prefix, address)
                )

        for cli_name in TRAP_TYPE_NAMES:
            field = cli_name.replace("-", "_")
            w_val = want.get(field)
            h_val = have.get(field)
            if w_val is True and h_val is not True:
                self.commands.append(
                    "configure trap %s %s %s" % (prefix, address, cli_name)
                )
            elif w_val is False and h_val is True:
                self.commands.append(
                    "configure trap %s %s no %s" % (prefix, address, cli_name)
                )

        for field, cli_name in SHAPING_FIELDS:
            w_val = want.get(field)
            h_val = have.get(field)
            if w_val is not None and w_val != "" and w_val != h_val:
                self.commands.append(
                    "configure trap %s %s %s %s" % (prefix, address, cli_name, w_val)
                )
            elif (w_val is None or w_val == "") and h_val is not None and h_val != "":
                self.commands.append(
                    "configure trap %s %s no %s" % (prefix, address, cli_name)
                )
