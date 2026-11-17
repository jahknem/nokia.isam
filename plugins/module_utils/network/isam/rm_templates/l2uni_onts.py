# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Parser/renderer for ``configure l2uni ont`` (per-UNI PM settings and TC-layer thresholds).

Device forms (``info configure l2uni [detail] flat``)::

    configure l2uni ont performance-monitor 1/1/2/1/1/1/1 no pm-collect no pm-collect-64bit
    configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect-ext no pm-collect no p-bits no vlan-id
    configure l2uni ont tc-layer-threshold 1/1/2/1/1/1/1 no dropped-frames-up no dropped-frames-dn

The small engine here (``UniPmNode`` / ``UniPmTemplate``) is shared with
``configure uni ont tc-layer`` (rm_templates/uni_onts.py): one node per CLI
command, keyed by the UNI index, with packed ``[no] <attr> [<value>]`` fields and
optional sub-nodes (``pm-collect-ext``). A field at its CLI default (shown as
``no <attr>``) is not reported, like an unset field.
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)

_TOKEN = re.compile(r'"[^"]*"|\S+')
IDENTITY = "uni_idx"


class UniPmField(object):
    """One ``[no] <cli> <value>`` attribute.

    kind: "str" or "int"; default: the CLI default (what ``no <cli>`` means);
    keywords: device spellings mapped to values (e.g. "disabled" -> 4294967295).
    """

    def __init__(self, name, cli, kind, default, keywords=None):
        self.name, self.cli, self.kind, self.default = name, cli, kind, default
        self.keywords = keywords or {}

    def coerce(self, raw):
        if raw in self.keywords:
            return self.keywords[raw]
        if self.kind == "int":
            try:
                return int(raw, 0)
            except ValueError:
                return raw
        return raw

    def render(self, value):
        if value is None or value == self.default:
            return "no " + self.cli
        return "{0} {1}".format(self.cli, value)


class UniPmNode(object):
    """One CLI command keyed by UNI: ``<command> <uni> [<sub>] [no] <field> ...``.

    subs: {key: (cli token, [UniPmField, ...])} for sub-nodes such as pm-collect-ext.
    """

    def __init__(self, section, command, fields, subs=None):
        self.section, self.command, self.fields = section, command, fields
        self.subs = subs or {}

    def scopes(self):
        """(sub key or None, cli suffix or None, fields) for the node and its sub-nodes."""
        yield None, None, self.fields
        for key, (cli, fields) in self.subs.items():
            yield key, cli, fields

    def scope_command(self, uni, cli=None):
        cmd = "{0} {1}".format(self.command, uni)
        return cmd + " " + cli if cli else cmd


class UniPmTemplate(NetworkTemplate):
    """Shared parser for UNI PM nodes; subclasses set NODES."""

    NODES = ()
    PARSERS = [
        {"name": "uni_pm", "getval": re.compile(r"^$"), "setval": "", "result": {}},
    ]

    def __init__(self, lines=None, module=None):
        super(UniPmTemplate, self).__init__(lines=lines, tmplt=self, module=module)
        self.unknown = []

    def parse(self):
        """{section: {uni: entry}}; tokens that are not known fields go to self.unknown."""
        result = {}
        self.unknown = []
        for raw in self._lines or []:
            line = raw.strip()
            if not line.startswith("configure "):
                line = "configure " + line
            for node in self.NODES:
                if not line.startswith(node.command + " "):
                    continue
                tokens = _TOKEN.findall(line[len(node.command) + 1:])
                if not tokens:
                    break
                uni = tokens[0]
                entry = result.setdefault(node.section, {}).setdefault(uni, {IDENTITY: uni})
                target, fields, rest = entry, node.fields, tokens[1:]
                for key, (cli, sub_fields) in node.subs.items():
                    if rest and rest[0] == cli:
                        # Recorded even when every field is at its default, so the
                        # line is seen as consumed; remove_empties drops it later.
                        target, fields, rest = entry.setdefault(key, {}), sub_fields, rest[1:]
                        break
                self._parse_fields(line, target, fields, rest)
                break
        return result

    def _parse_fields(self, line, target, fields, tokens):
        by_cli = dict((field.cli, field) for field in fields)
        index = 0
        while index < len(tokens):
            negate = tokens[index] == "no"
            key_index = index + 1 if negate else index
            field = by_cli.get(tokens[key_index]) if key_index < len(tokens) else None
            if field is None:
                self.unknown.append((line, tokens[index]))
                index += 1
                continue
            if negate:
                target.pop(field.name, None)
                index = key_index + 1
                continue
            if key_index + 1 >= len(tokens):
                self.unknown.append((line, tokens[key_index]))
                break
            value = field.coerce(tokens[key_index + 1].strip('"'))
            if value == field.default:
                target.pop(field.name, None)
            else:
                target[field.name] = value
            index = key_index + 2


def tca_threshold(name, cli):
    return UniPmField(name, cli, "int", 4294967295, keywords={"disabled": 4294967295})


L2UNI_NODES = (
    UniPmNode(
        "performance_monitor", "configure l2uni ont performance-monitor",
        [
            UniPmField("pm_collect", "pm-collect", "str", "none"),
            UniPmField("pm_collect_64bit", "pm-collect-64bit", "str", "none"),
        ],
        subs={
            "pm_collect_ext": ("pm-collect-ext", [
                UniPmField("pm_collect", "pm-collect", "str", "disable"),
                UniPmField("p_bits", "p-bits", "int", 255),
                UniPmField("vlan_id", "vlan-id", "int", 0),
            ]),
        },
    ),
    UniPmNode(
        "tc_layer_threshold", "configure l2uni ont tc-layer-threshold",
        [
            tca_threshold("dropped_frames_up", "dropped-frames-up"),
            tca_threshold("dropped_frames_dn", "dropped-frames-dn"),
        ],
    ),
)


class L2uni_ontsTemplate(UniPmTemplate):
    NODES = L2UNI_NODES
