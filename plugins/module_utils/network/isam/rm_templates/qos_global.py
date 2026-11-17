# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Parser/renderer for the global ``configure qos`` settings (isam_qos_global).

Owned lines (other qos families own interface/profiles/tca and the maps)::

    configure qos [no] atm-overhead-fact ... [no] set-dei          (general)
    configure qos global <lt> [no] buffer-occ-thresh ...            (line_cards)
    configure qos dsl-ctrl-pkt-policer [no] sustained-rate ...
    configure qos nni-ctrl-pkt-policer [no] sustained-rate ...
    configure qos ctrl-pkt-policer <protocol> [no] sustained-rate ...
    configure qos pbit-scheduling [no] sc-xcon-us ...
    configure qos upstr-prot-dsl [no] enable

``parse`` returns what the lines say, defaults included (``no X`` is the default
value); ``strip_defaults`` removes values equal to the known defaults, so facts
are the same for ``info ... flat`` and ``info ... flat detail``. Unknown keywords
and unknown enum values are skipped, never an error.
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)

_PBIT = ("svlanpbitbased", "cvlanpbitbased")

# section -> ordered [(cli keyword, option, type, default)]; type: "bool", "int" or a tuple of choices.
SECTION_ATTRS = {
    "general": [
        ("atm-overhead-fact", "atm_overhead_fact", "int", 85),
        ("eth-efm-fact", "eth_efm_fact", "int", 97),
        ("enable-alignment", "enable_alignment", "bool", False),
        ("cac-mode", "cac_mode", ("nocac", "msr", "alr"), "msr"),
        ("use-dei", "use_dei", "bool", False),
        ("set-dei", "set_dei", "bool", False),
    ],
    "line_cards": [
        ("buffer-occ-thresh", "buffer_occ_thresh", "int", 0),
        ("queue-stats", "queue_stats", "bool", False),
        ("dsload-tca", "dsload_tca", "bool", False),
        ("dsload-thresh", "dsload_thresh", "int", 0),
        ("buffer-tca", "buffer_tca", "bool", False),
        ("up-buf-thresh", "up_buf_thresh", "int", 0),
        ("up-obc-thresh", "up_obc_thresh", "int", 0),
        ("dn-obc-thresh", "dn_obc_thresh", "int", 0),
        ("dn-buf-thresh", "dn_buf_thresh", "int", 0),
        ("part-buf-thresh", "part_buf_thresh", "int", 0),
    ],
    "dsl_ctrl_pkt_policer": [
        ("sustained-rate", "sustained_rate", "int", 15),
        ("burst-size", "burst_size", "int", 10),
        ("protocol-ctrl", "protocol_ctrl", ("police-arprip", "nopolice-arprip"), "police-arprip"),
    ],
    "nni_ctrl_pkt_policer": [
        ("sustained-rate", "sustained_rate", "int", 64),
        ("burst-size", "burst_size", "int", 128),
    ],
    "ctrl_pkt_policer": [
        ("sustained-rate", "sustained_rate", "int", 15),
        ("burst-size", "burst_size", "int", 10),
    ],
    "pbit_scheduling": [
        ("sc-xcon-us", "sc_xcon_us", _PBIT, "svlanpbitbased"),
        ("sc-xcon-dn", "sc_xcon_dn", _PBIT, "svlanpbitbased"),
        ("sc-rb-us", "sc_rb_us", _PBIT, "svlanpbitbased"),
        ("sc-rb-dn", "sc_rb_dn", _PBIT, "cvlanpbitbased"),
    ],
    "upstr_prot_dsl": [
        ("enable", "enable", "bool", False),
    ],
}

# Settings sections (one dict each) and their CLI node below "configure qos".
SETTINGS_NODES = {
    "dsl_ctrl_pkt_policer": "dsl-ctrl-pkt-policer",
    "nni_ctrl_pkt_policer": "nni-ctrl-pkt-policer",
    "pbit_scheduling": "pbit-scheduling",
    "upstr_prot_dsl": "upstr-prot-dsl",
}
# List sections: CLI node and identity option.
LIST_NODES = {
    "line_cards": ("global", "name"),
    "ctrl_pkt_policer": ("ctrl-pkt-policer", "protocol"),
}
SECTIONS = ("general", "line_cards", "dsl_ctrl_pkt_policer", "nni_ctrl_pkt_policer",
            "ctrl_pkt_policer", "pbit_scheduling", "upstr_prot_dsl")

DEFAULTS = dict((section, dict((opt, default) for _kw, opt, _t, default in attrs))
                for section, attrs in SECTION_ATTRS.items())
ATTR_NAMES = dict((section, [opt for _kw, opt, _t, _d in attrs]) for section, attrs in SECTION_ATTRS.items())
_BY_KEYWORD = dict((section, dict((kw, (opt, typ)) for kw, opt, typ, _d in attrs))
                   for section, attrs in SECTION_ATTRS.items())
_BY_OPTION = dict((section, dict((opt, (kw, typ)) for kw, opt, typ, _d in attrs))
                  for section, attrs in SECTION_ATTRS.items())
_NODE_SECTION = dict((node, section) for section, node in SETTINGS_NODES.items())
_LT = re.compile(r"^\d+/\d+/\d+$")


def normalize_line_card(name):
    """``1/1/2`` -> ``lt:1/1/2`` (the form the device prints); anything else unchanged."""
    name = str(name).strip()
    return "lt:" + name if _LT.match(name) else name


def _scan(section, tokens, entry):
    """Apply ``[no] keyword [value]`` tokens to entry; unknown tokens are skipped."""
    spec = _BY_KEYWORD[section]
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == "no" and i + 1 < len(tokens) and tokens[i + 1] in spec:
            opt, typ = spec[tokens[i + 1]]
            entry[opt] = DEFAULTS[section][opt]
            i += 2
            continue
        if tok not in spec:
            i += 1
            continue
        opt, typ = spec[tok]
        if typ == "bool":
            entry[opt] = True
            i += 1
            continue
        value = tokens[i + 1] if i + 1 < len(tokens) else None
        if value is not None and typ == "int":
            try:
                entry[opt] = int(value)
            except ValueError:
                pass
        elif value is not None and value in typ:
            entry[opt] = value
        i += 2


def strip_defaults(parsed):
    """Drop values equal to the known defaults; line cards left without a value are dropped.

    ctrl-pkt-policer entries are created per protocol and stay even with defaults only.
    """
    result = {}
    for section in SECTIONS:
        value = parsed.get(section)
        if value is None:
            continue
        defaults = DEFAULTS[section]
        if section in LIST_NODES:
            key = LIST_NODES[section][1]
            items = []
            for item in value:
                kept = dict((k, v) for k, v in item.items() if k == key or v != defaults.get(k))
                if section == "line_cards" and len(kept) == 1:
                    continue
                items.append(kept)
            if items:
                result[section] = items
        else:
            kept = dict((k, v) for k, v in value.items() if v != defaults.get(k))
            if kept:
                result[section] = kept
    return result


class Qos_globalTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Qos_globalTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    def parse(self):
        result = {}
        lists = {"line_cards": {}, "ctrl_pkt_policer": {}}
        for raw in self._lines:
            line = raw.strip()
            if not line.startswith("configure qos "):
                continue
            tokens = line.split()[2:]
            if not tokens:
                continue
            head = tokens[0]
            if head == "global" and len(tokens) > 1:
                name = normalize_line_card(tokens[1])
                entry = lists["line_cards"].setdefault(name, {"name": name})
                _scan("line_cards", tokens[2:], entry)
            elif head == "ctrl-pkt-policer" and len(tokens) > 1:
                entry = lists["ctrl_pkt_policer"].setdefault(tokens[1], {"protocol": tokens[1]})
                _scan("ctrl_pkt_policer", tokens[2:], entry)
            elif head in _NODE_SECTION:
                _scan(_NODE_SECTION[head], tokens[1:], result.setdefault(_NODE_SECTION[head], {}))
            elif head == "no" or head in _BY_KEYWORD["general"]:
                if head == "no" and len(tokens) > 1 and tokens[1] == "ctrl-pkt-policer":
                    continue  # a removal command, not a setting
                _scan("general", tokens, result.setdefault("general", {}))
            # anything else (interface, profiles, tca, maps, unknown nodes) belongs elsewhere
        for section, entries in lists.items():
            if entries:
                result[section] = [entries[k] for k in sorted(entries)]
        return result

    # ----- rendering -------------------------------------------------------------------
    @staticmethod
    def token(section, option, value):
        """``kw value`` / ``kw`` / ``no kw``; value None resets to the default (``no kw``)."""
        kw, typ = _BY_OPTION[section][option]
        if value is None or (typ == "bool" and value is False):
            return "no " + kw
        if typ == "bool":
            return kw
        return "{0} {1}".format(kw, value)

    @staticmethod
    def prefix(section, identity=None):
        if section == "general":
            return "configure qos"
        if section in SETTINGS_NODES:
            return "configure qos " + SETTINGS_NODES[section]
        return "configure qos {0} {1}".format(LIST_NODES[section][0], identity)

    @staticmethod
    def command(section, tokens, identity=None):
        """One packed command for a section/entry; None without tokens."""
        prefix = Qos_globalTemplate.prefix(section, identity)
        if not tokens:
            return prefix if section == "ctrl_pkt_policer" else None
        return prefix + " " + " ".join(tokens)

    @staticmethod
    def remove_ctrl_pkt_policer(protocol):
        return "configure qos no ctrl-pkt-policer {0}".format(protocol)

    PARSERS = [
        {"name": "qos_global", "getval": re.compile(r"^$"), "setval": "", "result": {}},
    ]
