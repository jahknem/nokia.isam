# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Xdsl_bondingTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Xdsl_bondingTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "group_assembly_time",
            "getval": re.compile(
                r"^configure\sxdsl-bonding\sgroup-assembly-time\s(?P<group_assembly_time>\d+)$"
            ),
            "setval": "configure xdsl-bonding group-assembly-time {{ group_assembly_time }}",
            "remval": "configure xdsl-bonding group-assembly-time",
            "result": {
                "group_assembly_time": "{{ group_assembly_time|int }}",
            },
        },
        # configure xdsl-bonding group-assembly-time <sec> [ no ptm-init-mode | ptm-init-mode <mode> ]
        # The assembly time is mandatory in this command, so the config class passes the effective one.
        {
            "name": "ptm_init_mode",
            "getval": re.compile(
                r"^configure\s+xdsl-bonding\s+group-assembly-time\s+\d+\s+ptm-init-mode\s+(?P<ptm_init_mode>\S+)$"
            ),
            "setval": "configure xdsl-bonding group-assembly-time {{ group_assembly_time }} ptm-init-mode {{ ptm_init_mode }}",
            "remval": "configure xdsl-bonding group-assembly-time {{ group_assembly_time }} no ptm-init-mode",
            "result": {
                "ptm_init_mode": "{{ ptm_init_mode }}",
            },
        },
        # configure xdsl-bonding group (bonding-group-idx) [ no group-profile | group-profile <p> ]
        #   [ no group-rtx-profile | group-rtx-profile <p> ] [ [ no ] admin-up ] [ [ no ] up ]
        {
            "name": "group.group_profile",
            "compval": "group_profile",
            "getval": re.compile(
                r"^configure\s+xdsl-bonding\s+group\s+(?P<group_id>\S+)\s+group-profile\s+(?P<group_profile>\S+)$"
            ),
            "setval": "configure xdsl-bonding group {{ group_id }} group-profile {{ group_profile }}",
            "remval": "configure xdsl-bonding group {{ group_id }} no group-profile",
            "result": {
                "groups": {"{{ group_id }}": {"group_id": "{{ group_id }}", "group_profile": "{{ group_profile }}"}},
            },
        },
        {
            "name": "group.group_rtx_profile",
            "compval": "group_rtx_profile",
            "getval": re.compile(
                r"^configure\s+xdsl-bonding\s+group\s+(?P<group_id>\S+)\s+group-rtx-profile\s+(?P<group_rtx_profile>\S+)$"
            ),
            "setval": "configure xdsl-bonding group {{ group_id }} group-rtx-profile {{ group_rtx_profile }}",
            "remval": "configure xdsl-bonding group {{ group_id }} no group-rtx-profile",
            "result": {
                "groups": {"{{ group_id }}": {"group_id": "{{ group_id }}", "group_rtx_profile": "{{ group_rtx_profile }}"}},
            },
        },
        {
            "name": "group.up",
            "compval": "up",
            "getval": re.compile(r"^configure\s+xdsl-bonding\s+group\s+(?P<group_id>\S+)\s+up$"),
            "setval": "configure xdsl-bonding group {{ group_id }} up",
            "remval": "configure xdsl-bonding group {{ group_id }} no up",
            "result": {
                "groups": {"{{ group_id }}": {"group_id": "{{ group_id }}", "up": True}},
            },
        },
        # configure xdsl-bonding board (board-index) vect-fallback [ no group-profile | group-profile <p> ]
        #   [ no group-rtx-profile | group-rtx-profile <p> ]
        {
            "name": "board.vect_fallback.group_profile",
            "compval": "vect_fallback.group_profile",
            "getval": re.compile(
                r"^configure\s+xdsl-bonding\s+board\s+(?P<board_id>\S+)\s+vect-fallback\s+group-profile\s+(?P<group_profile>\S+)$"
            ),
            "setval": "configure xdsl-bonding board {{ board_id }} vect-fallback group-profile {{ vect_fallback.group_profile }}",
            "remval": "configure xdsl-bonding board {{ board_id }} vect-fallback no group-profile",
            "result": {
                "boards": {"{{ board_id }}": {"board_id": "{{ board_id }}", "vect_fallback": {"group_profile": "{{ group_profile }}"}}},
            },
        },
        {
            "name": "board.vect_fallback.group_rtx_profile",
            "compval": "vect_fallback.group_rtx_profile",
            "getval": re.compile(
                r"^configure\s+xdsl-bonding\s+board\s+(?P<board_id>\S+)\s+vect-fallback\s+group-rtx-profile\s+(?P<group_rtx_profile>\S+)$"
            ),
            "setval": "configure xdsl-bonding board {{ board_id }} vect-fallback group-rtx-profile {{ vect_fallback.group_rtx_profile }}",
            "remval": "configure xdsl-bonding board {{ board_id }} vect-fallback no group-rtx-profile",
            "result": {
                "boards": {
                    "{{ board_id }}": {"board_id": "{{ board_id }}", "vect_fallback": {"group_rtx_profile": "{{ group_rtx_profile }}"}},
                },
            },
        },
    ]
    # fmt: on
