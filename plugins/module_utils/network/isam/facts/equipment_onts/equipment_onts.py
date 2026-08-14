# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import shlex

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_scoped_config,
    unwrap_response,
    validate_config_safe,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.equipment_onts.equipment_onts import (
    Equipment_ontsArgs,
)


class Equipment_ontsFacts(object):
    """The isam equipment_onts facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Equipment_ontsArgs.argument_spec

    def get_config(self, connection):
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
        # Software-control entries are not scoped by an ONT identity.
        if config.get("sw_ctrls"):
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

    def _parse_config(self, config):
        result = {"interfaces": [], "slots": [], "sw_ctrls": []}
        current = None
        current_type = None

        if not config:
            return result

        lines = [line.strip() for line in str(config).splitlines() if line.strip()]
        if any(line.startswith("configure equipment ont ") for line in lines):
            expanded = []
            for line in lines:
                if line.startswith("configure equipment ont "):
                    expanded.extend(self._split_interface_line(line.replace("configure equipment ont ", "", 1)))
            config = "\n".join(expanded)

        for raw_line in config.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith("echo"):
                continue
            if line in ("configure equipment", "ont"):
                continue
            if line == "exit":
                if current is not None:
                    result[current_type].append(current)
                    current = None
                    current_type = None
                continue

            parts = line.split()
            if parts[0] == "interface" and len(parts) >= 2:
                if (
                    current_type == "interfaces"
                    and current is not None
                    and current.get("ont_idx") == parts[1]
                ):
                    if parts[2:] and not any(word in self._INTERFACE_WORDS for word in parts[2:]):
                        continue
                    self._set_pairs(current, parts[2:])
                    continue
                if current is not None:
                    result[current_type].append(current)
                current_type = "interfaces"
                current = {"ont_idx": parts[1]}
                self._set_pairs(current, parts[2:])
            elif parts[0] == "slot" and len(parts) >= 2:
                if (
                    current_type == "slots"
                    and current is not None
                    and current.get("ont_slot_idx") == parts[1]
                ):
                    if parts[2:] and not any(word in self._SLOT_WORDS for word in parts[2:]):
                        continue
                    self._set_pairs(current, parts[2:])
                    continue
                if current is not None:
                    result[current_type].append(current)
                current_type = "slots"
                current = {"ont_slot_idx": parts[1]}
                self._set_pairs(current, parts[2:])
            elif parts[0] == "sw-ctrl" and len(parts) >= 2:
                if (
                    current_type == "sw_ctrls"
                    and current is not None
                    and current.get("sw_ctrl_id") == int(parts[1])
                ):
                    self._set_pairs(current, parts[2:])
                    continue
                if current is not None:
                    result[current_type].append(current)
                current_type = "sw_ctrls"
                current = {"sw_ctrl_id": int(parts[1])}
                self._set_pairs(current, parts[2:])
            elif current is not None:
                words = (
                    self._INTERFACE_WORDS
                    if current_type == "interfaces"
                    else self._SLOT_WORDS
                    if current_type == "slots"
                    else self._SW_CTRL_WORDS
                )
                if any(word in words for word in parts):
                    self._set_pairs(current, parts)

        if current is not None:
            result[current_type].append(current)

        return result

    _INTERFACE_WORDS = {
        "sw-ver-pland", "battery-bkup", "berint", "desc1", "desc2", "provversion",
        "sernum", "subslocid", "fec-up", "bridge-map-mode", "pwr-shed-prof-id",
        "ont-enable", "p2p-enable", "optics-hist", "sw-dnload-version", "plnd-var",
        "rf-filter", "us-police-mode", "enable-aes", "voip-allowed", "iphc-allowed",
        "log-auth-id", "log-auth-pwd", "cvlantrans-mode", "sn-bundle-ctrl",
        "pland-cfgfile1", "pland-cfgfile2", "dnload-cfgfile1", "dnload-cfgfile2",
        "us-tcpolice-mode", "planned-us-rate", "oltdscppbitalign", "ratelimit-us-dhcp",
        "ratelimit-us-arp", "flush-mac", "template-name", "evtocd", "vtfd",
        "slid-visibility", "pwr-shed-prof-name", "admin-state",
    }
    _SLOT_WORDS = {
        "planned-card-type", "plndnumdataports", "plndnumvoiceports",
        "port-type", "transp-mode-rem", "no-mcast-control", "admin-state",
    }
    _SW_CTRL_WORDS = {
        "hw-version", "ont-variant", "plnd-sw-version", "plnd-sw-ver-conf",
        "sw-dwload-ver",
    }

    def _split_interface_line(self, line):
        tokens = shlex.split(line)
        if len(tokens) < 4 or tokens[0] != "interface":
            return [line]
        starts = [
            index for index, token in enumerate(tokens[2:], 2)
            if (token in self._INTERFACE_WORDS and (index == 2 or tokens[index - 1] != "no"))
            or (token == "no" and index + 1 < len(tokens) and tokens[index + 1] in self._INTERFACE_WORDS)
        ]
        if not starts:
            return [line]
        prefix = " ".join(tokens[:2])
        segments = [
            " ".join(tokens[start:end])
            for start, end in zip(starts, starts[1:] + [len(tokens)])
        ]
        return [prefix + " " + segments[0]] + segments[1:]

    def _set_pairs(self, item, parts):
        if len(parts) >= 2 and parts[0] == "no" and (
            parts[1] in self._INTERFACE_WORDS or parts[1] in self._SLOT_WORDS
        ):
            # An absent optional value must remain absent.  Passing None into
            # Ansible choice validation is invalid for fields such as
            # bridge-map-mode and admin-state.
            return
        idx = 0
        while idx < len(parts):
            words = self._INTERFACE_WORDS | self._SLOT_WORDS | self._SW_CTRL_WORDS
            if parts[idx] == "no" and idx + 1 < len(parts) and parts[idx + 1] in words:
                idx += 2
                continue
            key = parts[idx].replace("-", "_")
            if idx + 1 >= len(parts):
                item[key] = True
                idx += 1
                continue
            value = parts[idx + 1]
            if key in ("plndnumdataports", "plndnumvoiceports"):
                value = int(value)
            item[key] = value
            idx += 2
