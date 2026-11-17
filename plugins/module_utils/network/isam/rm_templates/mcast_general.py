# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.settings_block import (
    node_regex,
    parse_clauses,
    render_clause,
    settings_commands,
)

# configure mcast capacity [ no max-num-group | max-num-group <n> ] [ no max-num-uncfg | max-num-uncfg <n> ]
#   [ no cfg-res-time | cfg-res-time <s> ] [ no uncfg-res-time | uncfg-res-time <s> ]
# (option, CLI keyword, kind, device default) from the ISAM CLI command guide.
CAPACITY_ATTRS = (
    ("max_num_group", "max-num-group", "int", 1024),
    ("max_num_uncfg", "max-num-uncfg", "int", 64),
    ("cfg_res_time", "cfg-res-time", "int", 125),
    ("uncfg_res_time", "uncfg-res-time", "int", 0),
)
CAPACITY_LINE = node_regex("mcast capacity", CAPACITY_ATTRS)


def parse_capacity(line, capacity):
    """Apply one ``configure mcast capacity`` line to capacity; False when it is no capacity line.

    Defaults are not reported (``no <kw>`` or ``<kw> <default>`` remove the key);
    unknown keywords are ignored.
    """
    match = CAPACITY_LINE.match(line.strip())
    if not match:
        return False
    rest = match.group("rest") or ""
    tokens = rest.split()
    for option, cli, _kind, _default in CAPACITY_ATTRS:
        if cli in tokens:
            capacity.pop(option, None)
    capacity.update(parse_clauses(rest, CAPACITY_ATTRS))
    return True


def render_capacity(option, value):
    """``configure mcast capacity <kw> <value>``; value None renders the reset form."""
    return "configure mcast capacity " + render_clause(CAPACITY_ATTRS, option, value)


def capacity_commands(state, want, have):
    return settings_commands(state, want, have, CAPACITY_ATTRS, render_capacity)


class Mcast_generalTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Mcast_generalTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "admin_state",
            "compval": "admin_state",
            "getval": re.compile(
                r"^configure\smcast\sgeneral\s(?P<negate>no\s)?(?P<admin_state>admin-state)$"
            ),
            "setval": "configure mcast general {{ 'no ' if admin_state == false else '' }}admin-state",
            "result": {
                "admin_state": "{{ False if negate is defined else True }}",
            },
        },
        {
            "name": "forward_method",
            "compval": "forward_method",
            "getval": re.compile(
                r"^configure\smcast\sgeneral\sforward-method\s(?P<forward_method>\S+)$"
            ),
            "setval": "configure mcast general forward-method {{ forward_method }}",
            "result": {
                "forward_method": "{{ forward_method }}",
            },
        },
        {
            "name": "fast_change",
            "compval": "fast_change",
            "getval": re.compile(
                r"^configure\smcast\sgeneral\s(?P<negate>no\s)?(?P<fast_change>fast-change)(?:\s+.*)?$"
            ),
            "setval": "configure mcast general {{ 'no ' if fast_change == false else '' }}fast-change",
            "result": {
                "fast_change": "{{ False if negate is defined else True }}",
            },
        },
        {
            "name": "package_member",
            "compval": "package_member",
            "getval": re.compile(
                r"^configure\smcast\sgeneral\spackage-member\s(?P<package_member>.+)$"
            ),
            "setval": "configure mcast general package-member {{ package_member }}",
            "result": {
                "package_member": "{{ package_member }}",
            },
        },
    ]
    # fmt: on
