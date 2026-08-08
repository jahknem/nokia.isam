# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.voice_sip.voice_sip import (
    Isam_voice_sipArgs,
)


class Isam_voice_sipFacts(object):
    """The isam voice sip facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Isam_voice_sipArgs.argument_spec

    def get_config(self, connection):
        return connection.get("info configure voice sip flat")

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)
        data = unwrap_response(data)

        data = self._flatten_config(data)
        parsed = self._parse_voice_sip(data)

        ansible_facts["ansible_network_resources"].pop("voice_sip", None)
        params = utils.remove_empties(
            parsed
        ) or {}
        facts["voice_sip"] = params
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    @staticmethod
    def _flatten_config(config):
        flat_config = []
        if not config:
            return flat_config

        for raw_line in config.splitlines():
            line = raw_line.rstrip()
            # Strip comments (# preceded by space, not inside quoted values)
            if " #" in line:
                before = line[:line.index(" #")]
                if before.count('"') % 2 == 0:
                    line = before
            stripped = line.strip()
            if not stripped or stripped.startswith("echo") or stripped.startswith("#"):
                continue
            if line.startswith("configure voice sip "):
                flat_config.append(line)
        return flat_config

    @staticmethod
    def _parse_voice_sip(lines):
        result = {}

        for line in lines:
            if not line.startswith("configure voice sip "):
                continue
            rest = line[len("configure voice sip "):]
            parts = rest.split()

            if not parts:
                continue

            section = parts[0]

            if section == "lineid-syn-prof" and len(parts) >= 2:
                prof = parts[1]
                entry = {"name": prof}
                entry.update(Isam_voice_sipFacts._parse_bool_line(parts[2:],
                    ["syntax-pattern", "pots-syntax", "cas-r2-syntax", "cas-r1-syntax"],
                    {"isdn-syntax": "str"}))
                result.setdefault("lineid_syn_prof", {}).setdefault(prof, {"name": prof}).update(entry)

            elif section == "vsp" and len(parts) >= 2:
                vsp = parts[1]
                entry = {"name": vsp}
                Isam_voice_sipFacts._parse_vsp_line(parts[2:], entry)
                result.setdefault("vsp", {}).setdefault(vsp, {"name": vsp}).update(entry)

            elif section == "register" and len(parts) >= 2:
                reg = parts[1]
                entry = {"name": reg}
                entry.update(Isam_voice_sipFacts._parse_bool_line(parts[2:],
                    ["register-uri", "register-intv", "reg-retry-intv", "reg-prev-ava-intv",
                     "reg-head-start", "reg-start-min", "init-reg-delay"]))
                result.setdefault("register", {}).setdefault(reg, {"name": reg}).update(entry)

            elif section == "redundancy" and len(parts) >= 2:
                red = parts[1]
                entry = {"name": red}
                entry.update(Isam_voice_sipFacts._parse_bool_line(parts[2:],
                    ["support-redun", "dns-purge-timer", "dns-ini-retr-int", "dns-max-retr-nbr",
                     "fg-monitor-method", "fg-monitor-int", "bg-monitor-method", "bg-monitor-int",
                     "stable-obs-period", "fo-hystersis", "del-upd-threshold"]))
                result.setdefault("redundancy", {}).setdefault(red, {"name": red}).update(entry)

            elif section == "system":
                entry = {}
                entry.update(Isam_voice_sipFacts._parse_bool_line(parts[1:],
                    ["session-timer", "status", "min-se-time", "se-time", "admin-status"]))
                result.setdefault("system", {}).update(entry)

            elif section == "redundancy-cmd" and len(parts) >= 2:
                rcmd = parts[1]
                entry = {"name": rcmd}
                Isam_voice_sipFacts._parse_flat_value_line(parts[2:], entry,
                    {"fail-x-type": "str", "geo-fail-over": "str"},
                    ["start-time", "end-time"])
                result.setdefault("redundancy_cmd", {}).setdefault(rcmd, {"name": rcmd}).update(entry)

            elif section == "statistics":
                entry = {}
                if len(parts) > 1:
                    if parts[1] in ("stats-5min-config", "cdr-config"):
                        Isam_voice_sipFacts._parse_bool_line(parts[1:], entry, None,
                            ["stats-5min-config", "cdr-config"])
                    elif parts[1] == "stats-config":
                        rest_stats = parts[2:]
                        for token in rest_stats:
                            if token == "no":
                                continue
                            key = token.replace("-", "_")
                            entry[key] = True
                result.setdefault("statistics", {}).update(entry)

            elif section == "cas-nsm-prof" and len(parts) >= 2:
                prof = parts[1]
                entry = {"name": prof}
                Isam_voice_sipFacts._parse_flat_value_line(parts[2:], entry,
                    {"international-prefix": "str", "country-code": "str",
                     "outg-cpn-length": "int"},
                    ["version-nbr", "outg-from-no-cgpn", "national-prefix"])
                result.setdefault("cas_nsm_prof", {}).setdefault(prof, {"name": prof}).update(entry)

        # Convert keyed dicts to lists
        for key in ("lineid_syn_prof", "vsp", "register", "redundancy", "redundancy_cmd", "cas_nsm_prof"):
            if key in result:
                result[key] = list(result[key].values())

        return result

    @staticmethod
    def _parse_bool_line(tokens, bool_fields, typed_fields=None):
        entry = {}
        i = 0
        bool_field_set = set(bool_fields)
        typed_map = typed_fields or {}
        while i < len(tokens):
            token = tokens[i]
            negate = False
            if token == "no" and i + 1 < len(tokens):
                token = tokens[i + 1]
                negate = True
                i += 1
            if token in bool_field_set:
                entry[token.replace("-", "_")] = False if negate else True
            elif token in typed_map:
                if i + 1 < len(tokens):
                    val = tokens[i + 1]
                    if isinstance(val, str):
                        val = val.strip('"')
                    entry[token.replace("-", "_")] = val
                    if typed_map[token] == "int":
                        try:
                            entry[token.replace("-", "_")] = int(val)
                        except ValueError:
                            pass
                    i += 1
            i += 1
        return entry

    @staticmethod
    def _parse_flat_value_line(tokens, entry, str_fields, bool_fields=None):
        bool_field_set = set(bool_fields or [])
        i = 0
        while i < len(tokens):
            token = tokens[i]
            negate = False
            if token == "no" and i + 1 < len(tokens):
                token = tokens[i + 1]
                negate = True
                i += 1
            if token in str_fields:
                if i + 1 < len(tokens):
                    val = tokens[i + 1]
                    if isinstance(val, str):
                        val = val.strip('"')
                    key = token.replace("-", "_")
                    entry[key] = val
                    if str_fields[token] == "int":
                        try:
                            entry[key] = int(val)
                        except ValueError:
                            pass
                    i += 1
            elif token in bool_field_set:
                entry[token.replace("-", "_")] = False if negate else True
            i += 1

    @staticmethod
    def _parse_vsp_line(tokens, entry):
        bool_known = {"admin-status", "tinfo", "ta4", "ttir1", "t-acm-delta",
                       "access-held-time", "awaiting-time", "digit-send-mode",
                       "overlap-484-act", "dmpm-intdg"}
        str_fields = {"domain-name": "str"}
        int_fields = {"timer-b", "timer-f", "timer-t1", "timer-t2"}
        i = 0
        while i < len(tokens):
            token = tokens[i]
            negate = False
            if token == "no" and i + 1 < len(tokens):
                token = tokens[i + 1]
                negate = True
                i += 1
            if token in bool_known:
                entry[token.replace("-", "_")] = False if negate else True
            elif token in str_fields:
                if i + 1 < len(tokens):
                    val = tokens[i + 1]
                    if isinstance(val, str):
                        val = val.strip('"')
                    entry[token.replace("-", "_")] = val
                    i += 1
            elif token in int_fields:
                if i + 1 < len(tokens):
                    try:
                        entry[token.replace("-", "_")] = int(tokens[i + 1])
                    except ValueError:
                        pass
                    i += 1
            i += 1
