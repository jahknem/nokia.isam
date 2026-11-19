# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re
import time

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import covers_entry, is_masked_secret
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.equipment_onts.equipment_onts import Equipment_ontsFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import unwrap_response
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.equipment_onts import (
    INTERFACE_SUBNODES,
    LOOP_FIELDS,
    PM_COLLECT_FIELDS,
    SW_CTRL_EXTRA_FIELDS,
    SW_CTRL_SUBNODES,
    Equipment_ontsTemplate,
)

EMPTY = {"interfaces": [], "slots": [], "sw_ctrls": [], "loops": [], "pm_collects": []}


def _subnode_scopes(node, subnodes, unpacked=()):
    """Compaction scopes for a node and its subnodes: subnode settings are packed
    under their own scope, never into the node line; ``unpacked`` keywords are
    always sent as a line of their own."""
    names = "|".join(re.escape(cli) for _key, cli, _fields in subnodes)
    excluded = "|".join(re.escape(word) for word in tuple(unpacked) + tuple(cli for _k, cli, _f in subnodes))
    prefix = r"^(?P<scope>configure equipment ont %s \S+" % node
    return (
        prefix + r") (?P<suffix>(?!(?:%s)(?:\s|$)).+)$" % excluded,
        prefix + r" (?:%s)) (?P<suffix>.+)$" % names,
    )


class Equipment_onts(IsamResourceModule):
    """The isam_equipment_onts config class."""

    SHUTDOWN_VERIFY_ATTEMPTS = 5
    SHUTDOWN_VERIFY_INTERVAL = 1

    # admin-state is never packed: the device rejects it on the line that creates the
    # ONT ("invalid token") and prints it as a line of its own.
    COMPACT_COMMAND_SCOPES = (
        _subnode_scopes("interface", INTERFACE_SUBNODES, unpacked=("admin-state", "no admin-state"))
        + (r"^(?P<scope>configure equipment ont slot \S+) (?P<suffix>(?!(?:no\s+)?admin-state(?:\s|$)).+)$",)
        + _subnode_scopes("sw-ctrl", SW_CTRL_SUBNODES)
        + (
            r"^(?P<scope>configure equipment ont loop \S+) (?P<suffix>.+)$",
            r"^(?P<scope>configure equipment ont pm-collect \S+) (?P<suffix>.+)$",
        )
    )

    SECRET_FIELDS = ("log_auth_pwd",)
    # Interface values the device shows for an unset field; equal to unset when comparing.
    INTERFACE_DEFAULTS = {"subslocid": "WILDCARD"}
    INTERFACE_FIELDS = [
        "sw_ver_pland",
        "sernum",
        "subslocid",
        "fec_up",
        "sw_dnload_version",
        "plnd_var",
        "enable_aes",
        "log_auth_pwd",
        "cvlantrans_mode",
        "planned_us_rate",
        "bridge_map_mode",
        "ont_enable",
        "p2p_enable",
        "optics_hist",
        "voip_allowed",
        "iphc_allowed",
        "battery_bkup",
        "berint",
        "desc1",
        "desc2",
        "provversion",
        "pwr_shed_prof_id",
        "rf_filter",
        "us_police_mode",
        "slid_visibility",
        "log_auth_id",
        "sn_bundle_ctrl",
        "pland_cfgfile1",
        "pland_cfgfile2",
        "dnload_cfgfile1",
        "dnload_cfgfile2",
        "us_tcpolice_mode",
        "oltdscppbitalign",
        "ratelimit_us_dhcp",
        "ratelimit_us_arp",
        "flush_mac",
        "template_name",
        "evtocd",
        "vtfd",
        "pwr_shed_prof_name",
        "admin_state",
    ]
    SLOT_FIELDS = [
        "planned_card_type",
        "plndnumdataports",
        "plndnumvoiceports",
        "port_type",
        "transp_mode_rem",
        "no_mcast_control",
        "admin_state",
    ]
    SW_CTRL_FIELDS = [
        "hw_version",
        "ont_variant",
        "plnd_sw_version",
        "plnd_sw_ver_conf",
        "sw_dwload_ver",
    ] + [field for field, _cli in SW_CTRL_EXTRA_FIELDS]
    # Sub-node fields, compared as "<key>.<field>" (parser "<prefix>.<key>.<field>").
    INTERFACE_FIELDS = INTERFACE_FIELDS + [
        "%s.%s" % (key, field) for key, _cli, fields in INTERFACE_SUBNODES for field, _attr in fields
    ]
    SW_CTRL_FIELDS = SW_CTRL_FIELDS + [
        "%s.%s" % (key, field) for key, _cli, fields in SW_CTRL_SUBNODES for field, _attr in fields
    ]
    # ONT-keyed nodes without create/delete form: {field: CLI default}.
    LOOP_DEFAULTS = dict((field, default) for field, _cli, default in LOOP_FIELDS)
    PM_COLLECT_DEFAULTS = dict((field, default) for field, _cli, default in PM_COLLECT_FIELDS)

    def __init__(self, module):
        super(Equipment_onts, self).__init__(
            empty_fact_val=deepcopy(EMPTY),
            facts_module=Facts(module),
            module=module,
            resource="equipment_onts",
            tmplt=Equipment_ontsTemplate(),
        )

    def generate_commands(self):
        self._shutdown_targets = []
        want = self.want or deepcopy(EMPTY)
        have = self.have or deepcopy(EMPTY)
        # ResourceModule uses EMPTY when config is omitted. That mapping is truthy
        # even though every section is empty; test its contents, not the mapping.
        delete_all = self.state == "deleted" and not any(want.values())

        sections = [
            ("interfaces", "ont_idx", "interface", self.INTERFACE_FIELDS),
            ("slots", "ont_slot_idx", "slot", self.SLOT_FIELDS),
        ]
        # An ONT is built interface first, then its slots; it is removed the other way
        # round (the device refuses to delete an ONT that still has slots).
        if self.state == "deleted":
            self._shut_down_before_delete(want, have, delete_all)
            sections.reverse()
        for section, key, parser_prefix, fields in sections:
            self._compare_section(
                want.get(section) or [],
                have.get(section) or [],
                key,
                parser_prefix,
                fields,
                delete_all or bool(want.get(section)),
            )
        self._compare_section(
            want.get("sw_ctrls") or [],
            have.get("sw_ctrls") or [],
            "sw_ctrl_id",
            "sw_ctrl",
            self.SW_CTRL_FIELDS,
            delete_all or bool(want.get("sw_ctrls")),
        )
        # Loop / pm-collect settings go away with a removed ONT; resetting them
        # after "no interface" would address a non-existing ONT.
        removed = set(
            command.rsplit(" ", 1)[1] for command in self.commands
            if command.startswith("configure equipment ont no interface ")
        )
        for section, parser_prefix, defaults in (
            ("loops", "loop", self.LOOP_DEFAULTS),
            ("pm_collects", "pm_collect", self.PM_COLLECT_DEFAULTS),
        ):
            self._compare_ont_nodes(
                want.get(section) or [],
                have.get(section) or [],
                parser_prefix,
                defaults,
                delete_all or bool(want.get(section)),
                removed,
            )

    def _shut_down_before_delete(self, want, have, delete_all):
        """Admin-down what is about to be removed: the device refuses to delete an ONT
        or an ONT slot that is not admin down ("Not in admin down state to delete").
        Reassert even a gathered down state: interface and slot shutdown propagate
        independently, and a stale/detail read is not proof deletion is ready.
        """
        for section, key, node in (("interfaces", "ont_idx", "interface"), ("slots", "ont_slot_idx", "slot")):
            named = dict((item[key], item) for item in want.get(section) or [])
            for entry in have.get(section) or []:
                removed = delete_all or (entry[key] in named and covers_entry(named[entry[key]], entry, (key,)))
                if removed:
                    self.commands.append("configure equipment ont %s %s admin-state down" % (node, entry[key]))
                    self._shutdown_targets.append((section, key, node, entry[key]))

    def run_commands(self):
        if not self._shutdown_targets or self._module.check_mode:
            return super(Equipment_onts, self).run_commands()
        self._compact()
        accepted = []
        for command in self.commands:
            # Shutdowns form the prelude. Do not send a single removal until all
            # targeted interfaces AND slots have confirmed down after settling.
            if len(accepted) == len(self._shutdown_targets):
                self._verify_shutdown(accepted)
            self.changed = True  # a transport failure can still mean a write occurred
            try:
                self._connection.edit_config(candidate=[command])
            except Exception as exc:
                self._delete_failure(str(exc), accepted, failed_command=command, phase="execution")
            accepted.append(command)

    def _verify_shutdown(self, accepted):
        pending = list(self._shutdown_targets)
        parser = Equipment_ontsFacts(self._module)
        for _attempt in range(self.SHUTDOWN_VERIFY_ATTEMPTS):
            # Even an immediate config read can reflect the desired state before
            # the device permits deletion. Never poll in check mode or retry writes.
            time.sleep(self.SHUTDOWN_VERIFY_INTERVAL)
            remaining = []
            for section, key, node, identity in pending:
                command = "info configure equipment ont %s %s flat detail" % (node, identity)
                try:
                    response = unwrap_response(self._connection.get(command))
                except Exception as exc:
                    self._delete_failure("Shutdown readback failed: %s" % exc, accepted)
                entries = parser._parse_config(response).get(section, [])
                if not any(entry.get(key) == identity and entry.get("admin_state") == "down" for entry in entries):
                    remaining.append((section, key, node, identity))
            if not remaining:
                return
            pending = remaining
        self._delete_failure("Shutdown did not confirm admin-state down for %s" %
                             ", ".join("%s %s" % (node, identity) for _section, _key, node, identity in pending), accepted)

    def _delete_failure(self, message, accepted, failed_command=None, phase="shutdown_verification"):
        self._module.fail_json(
            msg="ONT deletion stopped: %s. Read back device state before retrying; no command was retried." % message,
            changed=self.changed,
            commands=self.commands,
            accepted=list(accepted),
            failed_command=failed_command,
            pending=self.commands[len(accepted) + (1 if failed_command is not None else 0):],
            failure_phase=phase,
            completion_status="unknown",
        )

    def _compare_ont_nodes(self, want_list, have_list, parser_prefix, defaults, requested, removed=()):
        """Loop / pm-collect nodes exist with their ONT: removal resets the fields.

        A value equal to the CLI default is the same as an unset field (the device
        prints both as ``no <attr>``).
        """
        def clean(entry):
            return dict(
                (key, value) for key, value in entry.items()
                if key == "ont_idx" or (value is not None and value != defaults.get(key))
            )

        wantd = dict((entry["ont_idx"], clean(entry)) for entry in want_list)
        haved = dict((entry["ont_idx"], clean(entry)) for entry in have_list if entry["ont_idx"] not in removed)
        fields = list(defaults)

        if self.state == "deleted":
            if not requested:
                return
            for ont_idx, have in iteritems(haved):
                if not wantd or ont_idx in wantd:
                    for field in fields:
                        if have.get(field) is not None:
                            self.addcmd(have, "%s.%s" % (parser_prefix, field), negate=True)
            return

        if self.state == "overridden":
            for ont_idx, have in iteritems(haved):
                if ont_idx not in wantd:
                    for field in fields:
                        if have.get(field) is not None:
                            self.addcmd(have, "%s.%s" % (parser_prefix, field), negate=True)

        for ont_idx, want in iteritems(wantd):
            self._compare_entry(want, haved.get(ont_idx, {"ont_idx": ont_idx}), parser_prefix, fields)

    def _compare_section(self, want_list, have_list, key, parser_prefix, fields, requested=True):
        wantd = {entry[key]: entry for entry in want_list}
        haved = {entry[key]: entry for entry in have_list}

        if self.state == "deleted":
            if not requested:
                return
            for item_key, have in iteritems(haved):
                if wantd and item_key not in wantd:
                    continue
                want = wantd.get(item_key, {})
                if covers_entry(want, have, (key,)):
                    self.addcmd(have, parser_prefix, negate=True)
                    continue
                # named settings only: reset them, the ONT / slot stays
                for field in fields:
                    if self._get(want, field) is not None and self._get(have, field) is not None:
                        self.addcmd(have, "%s.%s" % (parser_prefix, field), negate=True)
            return

        if self.state == "overridden":
            for item_key, have in iteritems(haved):
                if item_key not in wantd:
                    self.addcmd(have, parser_prefix, negate=True)

        for item_key, want in iteritems(wantd):
            have = haved.get(item_key, {})
            desired = deepcopy(want)
            if self.state == "merged" and have:
                desired = deepcopy(have)
                desired.update(want)
            if parser_prefix == "slot" and not have and self.state in ("merged", "rendered"):
                prefix = "configure equipment ont slot %s" % item_key
                command = prefix
                for field in self.SLOT_FIELDS:
                    if field != "admin_state" and desired.get(field) is not None:
                        command += " %s %s" % (field.replace("_", "-"), desired[field])
                # An admin-only request already addresses the slot; do not add a
                # bare navigation/creation line when there are no other options.
                if command != prefix or desired.get("admin_state") is None:
                    self.commands.append(command)
                if desired.get("admin_state") is not None:
                    self.addcmd(desired, "slot.admin_state")
                continue
            self._compare_entry(desired, have, parser_prefix, fields)

    @staticmethod
    def _get(entry, field):
        """Value of a field, or of "<sub-node>.<field>"."""
        for part in field.split("."):
            entry = entry.get(part) if isinstance(entry, dict) else None
        return entry

    def _compare_entry(self, want, have, parser_prefix, fields):
        for field in fields:
            inw = self._get(want, field)
            inh = self._get(have, field)
            if field in self.SECRET_FIELDS and (is_masked_secret(inw) or (inw is None and is_masked_secret(inh))):
                # The device only ever shows passwords masked, also when none is set: a
                # masked value is neither the password nor proof that one is set.
                continue
            if parser_prefix == "interface" and inh == self.INTERFACE_DEFAULTS.get(field) and inw is None:
                continue
            if inw is not None and inw != inh:
                self.addcmd(want, "%s.%s" % (parser_prefix, field))
            elif self.state in ("replaced", "overridden") and inw is None and inh is not None:
                self.addcmd(have, "%s.%s" % (parser_prefix, field), negate=True)
