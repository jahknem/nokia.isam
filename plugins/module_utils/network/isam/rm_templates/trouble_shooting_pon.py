# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Parser/renderer for ``configure trouble-shooting pon statistics``.

CLI help (ISAM CLI command guide, chapter "Trouble-Shooting Pon Interface"):

    configure trouble-shooting pon statistics ( no interface (if-index) ) | ( interface (if-index) )
    configure trouble-shooting pon statistics threshold [ no interval | interval <Gpon::TcaDetectIntval> ]
    configure trouble-shooting pon statistics threshold interface (if-index)
        [ no bw-th-up | bw-th-up <Gpon::TrbstBwThUp> ] [ no bw-th-dn | bw-th-dn <Gpon::TrbstBwThDn> ]

Detail output prints every PON port's thresholds (``no bw-th-up no bw-th-dn``) and
``threshold no interval``; defaults are not reported.
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.settings_block import (
    parse_clauses,
    render_clause,
)

BASE = "configure trouble-shooting pon statistics"
# (option, CLI keyword, kind, device default)
INTERVAL_ATTRS = (("interval", "interval", "int", 300),)
THRESHOLD_ATTRS = (
    ("bw_th_up", "bw-th-up", "int", 0),
    ("bw_th_dn", "bw-th-dn", "int", 0),
)

_HEAD = r"^(?:configure\s+)?trouble-shooting\s+pon\s+statistics\s+"
_STATS_IF = re.compile(_HEAD + r"interface\s+(?P<name>\S+)\s*$")
_THRESHOLD = re.compile(_HEAD + r"threshold(?:\s+(?P<rest>(?:no\s+)?interval(?:\s.*)?))?$")
_THRESHOLD_IF = re.compile(_HEAD + r"threshold\s+interface\s+(?P<name>\S+)(?:\s+(?P<rest>.*))?$")
LINE_REGEXES = (_STATS_IF, _THRESHOLD, _THRESHOLD_IF)


class Trouble_shooting_ponTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Trouble_shooting_ponTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    def parse(self):
        """{"interfaces": {name: {...}}, "interval": n, "thresholds": {name: {...}}}.

        Threshold entries at their defaults are kept (name only); the facts class
        drops them so detail and plain output give the same facts.
        """
        # The generic parse only matches PARSERS (empty results); it lets the
        # gather_configuration line tracker see lines that leave the result unchanged
        # (all defaults). Looked up at call time on purpose.
        NetworkTemplate.parse(self)
        result = {}
        for raw in self._lines:
            line = raw.strip()
            match = _STATS_IF.match(line)
            if match:
                result.setdefault("interfaces", {})[match.group("name")] = {"name": match.group("name")}
                continue
            match = _THRESHOLD_IF.match(line)
            if match:
                entry = result.setdefault("thresholds", {}).setdefault(match.group("name"), {"name": match.group("name")})
                tokens = (match.group("rest") or "").split()
                for option, cli, _kind, _default in THRESHOLD_ATTRS:
                    if cli in tokens:
                        entry.pop(option, None)
                entry.update(parse_clauses(match.group("rest"), THRESHOLD_ATTRS))
                continue
            match = _THRESHOLD.match(line)
            if match:
                if "interval" in (match.group("rest") or "").split():
                    result.pop("interval", None)
                result.update(parse_clauses(match.group("rest"), INTERVAL_ATTRS))
        return result

    @staticmethod
    def render_interface(name, enable=True):
        return "{0} {1}interface {2}".format(BASE, "" if enable else "no ", name)

    @staticmethod
    def render_interval(value):
        return "{0} threshold {1}".format(BASE, render_clause(INTERVAL_ATTRS, "interval", value))

    @staticmethod
    def render_threshold(name, option, value):
        return "{0} threshold interface {1} {2}".format(BASE, name, render_clause(THRESHOLD_ATTRS, option, value))

    PARSERS = [
        {"name": "statistics_interface", "getval": _STATS_IF, "setval": "", "result": {}},
        {"name": "threshold", "getval": _THRESHOLD, "setval": "", "result": {}},
        {"name": "threshold_interface", "getval": _THRESHOLD_IF, "setval": "", "result": {}},
    ]
