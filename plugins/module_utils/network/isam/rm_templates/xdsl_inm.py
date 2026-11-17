# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Parser/renderer for ``configure xdsl imp-noise-sensor near-end|far-end <line>``.

The device prints every attribute of one line packed on a single flat line
(``... no inm-mode no inm-eq-inp-mode ...`` in detail output), so the parser
tokenizes the remainder instead of using one regex per attribute.
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)

# (option, CLI keyword); all take one value, ``no <keyword>`` resets to the default.
ATTRS = (
    ("inm_mode", "inm-mode"),
    ("inm_eq_inp_mode", "inm-eq-inp-mode"),
    ("ins_sensitivity", "ins-sensitivity"),
    ("inm_cluster_cont", "inm-cluster-cont"),
    ("inm_iat_offset", "inm-iat-offset"),
    ("inm_iat_step", "inm-iat-step"),
)
# (option list, CLI direction)
SIDES = (("near_end", "near-end"), ("far_end", "far-end"))

_CLI_TO_ATTR = dict((cli, attr) for attr, cli in ATTRS)
_ATTR_TO_CLI = dict(ATTRS)
_SIDE_TO_LIST = dict((cli, side) for side, cli in SIDES)
_LIST_TO_SIDE = dict(SIDES)
_LINE = re.compile(
    r"^(?:configure\s+)?xdsl\s+imp-noise-sensor\s+(?P<side>near-end|far-end)\s+(?P<name>\S+)(?:\s+(?P<rest>.*))?$"
)


def parse_attributes(rest, entry, cli_to_attr, flags=()):
    """Apply packed ``[no] <keyword> [<value>]`` clauses to entry.

    Value keywords: ``<kw> <value>`` sets, ``no <kw>`` removes (device default).
    Flag keywords (flags): ``<kw>`` is True, ``no <kw>`` is False.
    Returns the tokens that were not understood.
    """
    tokens = (rest or "").split()
    unknown = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        negate = token == "no" and index + 1 < len(tokens) and tokens[index + 1] in cli_to_attr
        if negate:
            index += 1
            token = tokens[index]
        if token not in cli_to_attr:
            unknown.append(token)
            index += 1
            continue
        attr = cli_to_attr[token]
        if token in flags:
            entry[attr] = not negate
            index += 1
        elif negate:
            entry.pop(attr, None)
            index += 1
        elif index + 1 < len(tokens) and tokens[index + 1] not in cli_to_attr and tokens[index + 1] != "no":
            entry[attr] = tokens[index + 1]
            index += 2
        else:
            unknown.append(token)
            index += 1
    return unknown


class Xdsl_inmTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Xdsl_inmTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    def parse(self):
        """{"near_end": {line: entry}, "far_end": {line: entry}} for the lines given."""
        result = {}
        for raw in self._lines:
            match = _LINE.match(raw.strip())
            if not match:
                continue
            side = _SIDE_TO_LIST[match.group("side")]
            name = match.group("name")
            entry = result.setdefault(side, {}).setdefault(name, {"name": name})
            parse_attributes(match.group("rest"), entry, _CLI_TO_ATTR)
        return result

    @staticmethod
    def command(side, name, suffix=""):
        cmd = "configure xdsl imp-noise-sensor {0} {1}".format(_LIST_TO_SIDE[side], name)
        return cmd + (" " + suffix if suffix else "")

    @staticmethod
    def render_attr(side, entry, attr):
        """Set command for entry[attr], or its ``no`` form when the value is None."""
        cli = _ATTR_TO_CLI[attr]
        value = entry.get(attr)
        if value is None:
            return Xdsl_inmTemplate.command(side, entry["name"], "no " + cli)
        return Xdsl_inmTemplate.command(side, entry["name"], "{0} {1}".format(cli, value))

    PARSERS = [
        {"name": "xdsl_inm", "getval": re.compile(r"^$"), "setval": "", "result": {}},
    ]
