# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Shared parser/renderer for small global settings blocks.

A settings block is one CLI node without instances whose attributes are all
``[ no <keyword> | <keyword> <value> ]`` clauses, e.g. ``configure nat
[ no aging-time | aging-time <value> ]``. The detail output prints every
attribute, defaults as ``no <keyword>``; the plain output omits defaults.

Facts never report a known default: ``no <keyword>`` and ``<keyword> <default>``
both mean "absent". Unknown keywords are ignored, never an error.

The clause parsing and the per-attribute state decision come from the shared
attribute-table core (attribute_table.py); this module keeps the settings-block
specifics: the optional ``configure`` prefix, the line tracker, and one command per
attribute (the table families pack a node's clauses into one line instead).
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.attribute_table import (
    Attr,
    change,
    convert as _convert,
    parse_clauses as _parse_clauses,
)


def node_regex(node, attrs):
    """Line regex of a node: ``[configure ]<node>`` followed by a known clause (or nothing).

    Requiring a known first clause keeps sibling nodes out (``configure pon interface``
    is not a ``configure pon`` settings line).
    """
    keywords = "|".join(re.escape(cli) for _option, cli, _kind, _default in attrs)
    words = r"\s+".join(re.escape(word) for word in node.split())
    return re.compile(
        r"^(?:configure\s+)?" + words + r"(?:\s+(?P<rest>(?:no\s+)?(?:" + keywords + r")(?:\s.*)?))?$"
    )


def convert(kind, value):
    """Typed value of a parsed token (ints stay strings when they are not numeric)."""
    return _convert(kind, value)


def parse_clauses(rest, attrs):
    """{option: value} of the packed clauses, defaults and negated values dropped."""
    raw = _parse_clauses((rest or "").split(), tuple(Attr(option, cli, kind, default) for option, cli, kind, default in attrs))
    entry = {}
    for option, _cli, _kind, default in attrs:
        value = raw.get(option)
        if value is not None and value != default:
            entry[option] = value
    return entry


def render_clause(attrs, option, value):
    """``<keyword> <value>``, or ``no <keyword>`` for value None."""
    cli = [c for o, c, _k, _d in attrs if o == option][0]
    if value is None:
        return "no " + cli
    return "{0} {1}".format(cli, value)


def settings_commands(state, want, have, attrs, render):
    """Commands bringing one settings block from have to want.

    render(option, value) returns the full command; value None is the reset form.
    have holds only non-default values (absent means the device default).
    merged sets what differs; replaced/overridden also reset what want omits;
    deleted resets the attributes want names (any value, an explicit default too) or,
    when want names none (no config, an empty block), every non-default attribute
    (docs/development-style.md: named attributes reset only themselves). The
    per-attribute decision is the
    shared core ``change`` (a default have value counts as absent); rendered keeps
    the settings-block form (every given non-default value, one command each).
    """
    want = want or {}
    have = have or {}
    commands = []
    named = set(option for option, _cli, _kind, _default in attrs if want.get(option) is not None)
    for option, cli, kind, default in attrs:
        if state == "deleted" and named and option not in named:
            continue
        wv = want.get(option)
        hv = have.get(option)
        # Legacy settings blocks suppress defaults even in rendered. Unlike the
        # table renderer, that path has always made the merged-style decision.
        comparison_state = {"deleted": "replaced", "rendered": "merged"}.get(state, state)
        attr = Attr(option, cli, kind, default)
        tokens = change(attr, None if state == "deleted" else wv, None if hv == default else hv,
                        comparison_state)
        if tokens:
            commands.append(render(option, None if tokens[0] == "no" else wv))
    return commands


class SettingsBlockTemplate(NetworkTemplate):
    """Base template: subclasses set NODE (CLI node after ``configure``) and ATTRS.

    ATTRS: ((option, CLI keyword, kind "int"|"str", device default), ...).
    """

    NODE = ""
    ATTRS = ()
    PARSERS = []

    def __init__(self, lines=None, module=None):
        super(SettingsBlockTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    @classmethod
    def line_regex(cls):
        return node_regex(cls.NODE, cls.ATTRS)

    def parse(self):
        """{option: value} of all settings lines given (later lines win)."""
        # The generic parse only matches PARSERS (empty results); it lets the
        # gather_configuration line tracker see lines that leave the result unchanged
        # (all defaults). Looked up at call time on purpose.
        NetworkTemplate.parse(self)
        regex = self.line_regex()
        result = {}
        for raw in self._lines:
            match = regex.match(raw.strip())
            if not match:
                continue
            rest = match.group("rest") or ""
            tokens = rest.split()
            # a later line mentioning an attribute (also as ``no <kw>``) replaces it
            for option, cli, _kind, _default in self.ATTRS:
                if cli in tokens:
                    result.pop(option, None)
            result.update(parse_clauses(rest, self.ATTRS))
        return result

    @classmethod
    def render_attr(cls, option, value):
        """Set command for one attribute; value None renders the reset (``no``) form."""
        return "configure {0} {1}".format(cls.NODE, render_clause(cls.ATTRS, option, value))

    @classmethod
    def commands(cls, state, want, have):
        return settings_commands(state, want, have, cls.ATTRS, cls.render_attr)


def make_parsers(name, node, attrs):
    """PARSERS entry whose getval matches the settings lines (snapshot tracker, docs)."""
    return [{"name": name, "getval": node_regex(node, attrs), "setval": "", "result": {}}]
