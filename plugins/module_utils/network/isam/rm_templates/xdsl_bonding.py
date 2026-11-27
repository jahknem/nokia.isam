# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_inm import parse_attributes

# Per bonding group and per board; the device prints every attribute packed on flat
# lines (lab, 2026-11-27, 'info configure xdsl-bonding flat detail'):
#   configure xdsl-bonding group 1/1/3/1 no group-profile no group-rtx-profile
#   configure xdsl-bonding group 1/1/3/1 no up
#   configure xdsl-bonding board 1/1/3 vect-fallback no group-profile no group-rtx-profile
# (option, CLI keyword, flag)
GROUP_ATTRS = (("group_profile", "group-profile", False), ("group_rtx_profile", "group-rtx-profile", False),
               ("up", "up", True))
BOARD_ATTRS = (("vect_fallback", "vect-fallback", True), ("group_profile", "group-profile", False),
               ("group_rtx_profile", "group-rtx-profile", False))
SECTIONS = (("groups", "group", "group_id", GROUP_ATTRS), ("boards", "board", "board_id", BOARD_ATTRS))
_SECTION_LINE = re.compile(r"^(?:configure\s+)?xdsl-bonding\s+(?P<node>group|board)\s+(?P<id>\d+(?:/\d+)+)(?:\s+(?P<rest>.*))?$")


def parse_sections(lines):
    """{"groups": {group: entry}, "boards": {board: entry}} from flat lines. An instance
    line without attributes (or with defaults only) still yields its entry."""
    result = {}
    by_node = dict((node, (section, field, attrs)) for section, node, field, attrs in SECTIONS)
    for raw in lines or []:
        match = _SECTION_LINE.match(raw.strip())
        if not match:
            continue
        section, field, attrs = by_node[match.group("node")]
        identity = match.group("id")
        entry = result.setdefault(section, {}).setdefault(identity, {field: identity})
        cli_to_attr = dict((cli, attr) for attr, cli, _flag in attrs)
        flags = tuple(cli for _attr, cli, flag in attrs if flag)
        parse_attributes(match.group("rest"), entry, cli_to_attr, flags)
    return result


class Xdsl_bondingTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Xdsl_bondingTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "group_assembly_time",
            "getval": re.compile(
                # flat detail packs further settings after it ("... 0 no ptm-init-mode")
                r"^configure\sxdsl-bonding\sgroup-assembly-time\s(?P<group_assembly_time>\d+)(?:\s.*)?$"
            ),
            "setval": "configure xdsl-bonding group-assembly-time {{ group_assembly_time }}",
            "remval": "configure xdsl-bonding group-assembly-time",
            "result": {
                "group_assembly_time": "{{ group_assembly_time|int }}",
            },
        },
    ]
    # fmt: on
