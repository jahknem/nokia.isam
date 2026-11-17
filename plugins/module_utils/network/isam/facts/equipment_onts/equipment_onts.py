# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import re

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_scoped_config,
    get_targeted_config,
    unwrap_response,
    validate_config_safe,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.equipment_onts.equipment_onts import (
    Equipment_ontsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.equipment_onts import (
    INTERFACE_SUBNODES,
    LOOP_FIELDS,
    PM_COLLECT_FIELDS,
    SW_CTRL_EXTRA_FIELDS,
    SW_CTRL_SUBNODES,
)

_TOKEN = re.compile(r'"[^"]*"|\S+')
SECTIONS = ("interfaces", "slots", "sw_ctrls", "loops", "pm_collects")


def _cli_fields(names, defaults=None):
    """{CLI attribute: (field, default or None)} for names given as CLI attributes."""
    return dict((name, (name.replace("-", "_"), (defaults or {}).get(name))) for name in names)


class Equipment_ontsFacts(object):
    """The isam equipment_onts facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Equipment_ontsArgs.argument_spec

    def get_config(self, connection):
        if self._module.params.get("state") == "gathered":
            # Targeted gathering, software controls included.
            return get_targeted_config(self._module, connection, "equipment_onts", "info configure equipment ont flat", {
                "interfaces": "info configure equipment ont interface %s flat detail",
                "slots": "info configure equipment ont slot %s flat detail",
                "sw_ctrls": "info configure equipment ont sw-ctrl %s flat",
                "loops": "info configure equipment ont loop %s flat",
                "pm_collects": "info configure equipment ont pm-collect %s flat",
            })
        config = self._module.params.get("config") or {}
        commands = []
        for item in config.get("interfaces") or []:
            commands.append(
                "info configure equipment ont interface %s flat detail" % item["ont_idx"]
            )
        for item in config.get("slots") or []:
            commands.append(
                "info configure equipment ont slot %s flat detail" % item["ont_slot_idx"]
            )
        # Software-control entries are not scoped by an ONT identity; loop and
        # pm-collect entries are only read per instance with state gathered.
        if config.get("sw_ctrls") or config.get("loops") or config.get("pm_collects"):
            commands = []
        return get_scoped_config(
            self._module,
            connection,
            config,
            "info configure equipment ont flat",
            commands,
        )

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)
        data = unwrap_response(data)

        objs = self._parse_config(data)
        ansible_facts["ansible_network_resources"].pop("equipment_onts", None)
        params = utils.remove_empties(
            validate_config_safe(self.argument_spec, {"config": objs})
        )
        facts["equipment_onts"] = params.get("config", {})
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts

    # Node schema: kind -> (section, identity field, int identity, {CLI attr: (field, default)},
    # {sub-node CLI token: (key, {CLI attr: (field, default)})}). A field at its default
    # (non-None) is not reported; tokens that are no known attribute are dropped.
    _INTERFACE_WORDS = (
        "sw-ver-pland", "battery-bkup", "berint", "desc1", "desc2", "provversion",
        "sernum", "subslocid", "fec-up", "bridge-map-mode", "pwr-shed-prof-id",
        "ont-enable", "p2p-enable", "optics-hist", "sw-dnload-version", "plnd-var",
        "rf-filter", "us-police-mode", "enable-aes", "voip-allowed", "iphc-allowed",
        "log-auth-id", "log-auth-pwd", "cvlantrans-mode", "sn-bundle-ctrl",
        "pland-cfgfile1", "pland-cfgfile2", "dnload-cfgfile1", "dnload-cfgfile2",
        "us-tcpolice-mode", "planned-us-rate", "oltdscppbitalign", "ratelimit-us-dhcp",
        "ratelimit-us-arp", "flush-mac", "template-name", "evtocd", "vtfd",
        "slid-visibility", "pwr-shed-prof-name", "admin-state",
    )
    _SLOT_WORDS = (
        "planned-card-type", "plndnumdataports", "plndnumvoiceports",
        "port-type", "transp-mode-rem", "no-mcast-control", "admin-state",
    )
    _SW_CTRL_WORDS = (
        "hw-version", "ont-variant", "plnd-sw-version", "plnd-sw-ver-conf",
        "sw-dwload-ver",
    ) + tuple(cli for _field, cli in SW_CTRL_EXTRA_FIELDS)
    _INT_FIELDS = ("plndnumdataports", "plndnumvoiceports")

    @staticmethod
    def _subs(subnodes):
        return dict(
            (cli, (key, dict((attr, (field, None)) for field, attr in fields)))
            for key, cli, fields in subnodes
        )

    @classmethod
    def _nodes(cls):
        return {
            "interface": ("interfaces", "ont_idx", False, _cli_fields(cls._INTERFACE_WORDS), cls._subs(INTERFACE_SUBNODES)),
            "slot": ("slots", "ont_slot_idx", False, _cli_fields(cls._SLOT_WORDS), {}),
            "sw-ctrl": ("sw_ctrls", "sw_ctrl_id", True, _cli_fields(cls._SW_CTRL_WORDS), cls._subs(SW_CTRL_SUBNODES)),
            "loop": ("loops", "ont_idx", False, dict((cli, (field, default)) for field, cli, default in LOOP_FIELDS), {}),
            "pm-collect": ("pm_collects", "ont_idx", False, dict((cli, (field, default)) for field, cli, default in PM_COLLECT_FIELDS), {}),
        }

    def _parse_config(self, config):
        """Parse flat (``configure equipment ont <node> <id> ...``) or block output.

        Never fails on unknown keywords: tokens that are no modelled attribute are
        dropped (and recorded in self.unknown for diagnostics).
        """
        self.unknown = []
        nodes = self._nodes()
        entries = dict((section, {}) for section in SECTIONS)

        if not config:
            return dict((section, []) for section in SECTIONS)

        lines = [line.strip() for line in str(config).splitlines() if line.strip()]
        flat = any(line.startswith("configure equipment ont ") for line in lines)
        current = None  # (kind, identity) of the open block entry
        sub = None  # sub-node CLI token opened on its own block line
        for line in lines:
            if line.startswith("#") or line.startswith("echo"):
                continue
            if flat:
                if not line.startswith("configure equipment ont "):
                    continue
                tokens = _TOKEN.findall(line[len("configure equipment ont "):])
                if len(tokens) >= 2 and tokens[0] in nodes:
                    self._apply(nodes, entries, tokens[0], tokens[1], tokens[2:], line)
                elif tokens:
                    self.unknown.append((line, tokens[0]))
                continue
            if line in ("configure equipment", "ont", "configure equipment ont"):
                continue
            if line == "exit":
                if sub is not None:
                    sub = None
                else:
                    current = None
                continue
            tokens = _TOKEN.findall(line)
            if len(tokens) >= 2 and tokens[0] in nodes:
                current, sub = (tokens[0], tokens[1]), None
                self._apply(nodes, entries, tokens[0], tokens[1], tokens[2:], line)
            elif current is not None:
                kind, identity = current
                subs = nodes[kind][4]
                if tokens[0] in subs and len(tokens) == 1:
                    sub = tokens[0]
                    continue
                rest = [sub] + tokens if sub is not None and tokens[0] not in subs else tokens
                self._apply(nodes, entries, kind, identity, rest, line)
            else:
                self.unknown.append((line, tokens[0]))

        for section in ("loops", "pm_collects"):
            # These nodes exist with every ONT; one with only default values
            # (all "no <attr>", as detail prints it) has nothing to report.
            for identity in [ident for ident, entry in entries[section].items() if len(entry) == 1]:
                del entries[section][identity]
        return dict((section, list(entries[section].values())) for section in SECTIONS)

    def _apply(self, nodes, entries, kind, identity, tokens, line):
        section, key, int_identity, fields, subs = nodes[kind]
        if int_identity:
            try:
                identity = int(identity)
            except ValueError:
                self.unknown.append((line, identity))
                return
        entry = entries[section].setdefault(identity, {key: identity})
        target = entry
        if tokens and tokens[0] in subs:
            sub_key, fields = subs[tokens[0]]
            target = entry.setdefault(sub_key, {})
            tokens = tokens[1:]
        index = 0
        while index < len(tokens):
            negate = tokens[index] == "no"
            key_index = index + 1 if negate else index
            spec = fields.get(tokens[key_index]) if key_index < len(tokens) else None
            if spec is None:
                self.unknown.append((line, tokens[index]))
                index += 1
                continue
            field, default = spec
            if negate:
                target.pop(field, None)
                index = key_index + 1
                continue
            if key_index + 1 >= len(tokens):
                self.unknown.append((line, tokens[key_index]))
                break
            value = tokens[key_index + 1].strip('"')
            if field in self._INT_FIELDS:
                try:
                    value = int(value)
                except ValueError:
                    pass
            if default is not None and value == default:
                target.pop(field, None)
            else:
                target[field] = value
            index = key_index + 2
