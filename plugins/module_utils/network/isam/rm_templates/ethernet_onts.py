# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
Parser templates for the isam_ethernet_onts resource.
"""

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Ethernet_ontsTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Ethernet_ontsTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "ont.cust_info",
            "compval": "cust_info",
            "getval": re.compile(
                r"""
                configure\sethernet\sont\s(?P<uni_idx>\S+)\scust-info\s\"(?P<cust_info>(?:[^\"\\]|\\.)*)\"
                $""", re.VERBOSE),
            "setval": "configure ethernet ont {{ uni_idx }} cust-info \"{{ cust_info | replace('\\\"', '\\\\\\\"') }}\"",
            "remval": "configure ethernet ont {{ uni_idx }} no cust-info",
            "result": {
                "{{ uni_idx }}": {
                    "uni_idx": "{{ uni_idx }}",
                    "cust_info": "{{ cust_info }}",
                }
            },
        },
        {
            "name": "ont.cust_info_unquoted",
            "compval": "cust_info",
            "getval": re.compile(
                r"""
                configure\sethernet\sont\s(?P<uni_idx>\S+)\scust-info\s(?P<cust_info>\S.*?)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "{{ uni_idx }}": {
                    "uni_idx": "{{ uni_idx }}",
                    "cust_info": "{{ cust_info }}",
                }
            },
        },
        {
            "name": "ont.auto_detect",
            "compval": "auto_detect",
            "getval": re.compile(
                r"""
                configure\sethernet\sont\s(?P<uni_idx>\S+)\sauto-detect\s(?P<auto_detect>\S+)
                $""", re.VERBOSE),
            "setval": "configure ethernet ont {{ uni_idx }} auto-detect {{ auto_detect }}",
            # The CLI has no "no auto-detect": the value stays until the UNI goes away.
            "no_remval": True,
            "result": {
                "{{ uni_idx }}": {
                    "uni_idx": "{{ uni_idx }}",
                    "auto_detect": "{{ auto_detect }}",
                }
            },
        },
        {
            "name": "ont.admin_state",
            "compval": "admin_state",
            "getval": re.compile(
                r"""
                configure\sethernet\sont\s(?P<uni_idx>\S+)\sadmin-state\s(?P<admin_state>\S+)
                $""", re.VERBOSE),
            "setval": "configure ethernet ont {{ uni_idx }} admin-state {{ admin_state }}",
            "remval": "configure ethernet ont {{ uni_idx }} no admin-state",
            "result": {
                "{{ uni_idx }}": {
                    "uni_idx": "{{ uni_idx }}",
                    "admin_state": "{{ admin_state }}",
                }
            },
        },
    ]
    # fmt: on


def _value_parser(field, cli_name):
    return {
        "name": "ont." + field,
        "compval": field,
        "getval": re.compile(
            r"^configure\sethernet\sont\s(?P<uni_idx>\S+)\s"
            + re.escape(cli_name)
            + r"\s(?P<" + field + r">\S+)$"
        ),
        "setval": "configure ethernet ont {{ uni_idx }} " + cli_name + " {{ " + field + " }}",
        "remval": "configure ethernet ont {{ uni_idx }} no " + cli_name,
        "result": {
            "{{ uni_idx }}": {
                "uni_idx": "{{ uni_idx }}",
                field: "{{ " + field + " }}",
            }
        },
    }


Ethernet_ontsTemplate.PARSERS.extend(
    [
        _value_parser("power_control", "power-control"),
        _value_parser("pse_class", "pse-class"),
        _value_parser("pse_pw_priority", "pse-pw-priority"),
        _value_parser("pwr_override", "pwr-override"),
        _value_parser("lpt_mode", "lpt-mode"),
    ]
)


# Sub-nodes of the UNI (CLI reference "ONT Ethernet Port Configuration"):
#   configure ethernet ont (uni-idx) phy [ no pm | pm <enable|disable> ]
#   configure ethernet ont (uni-idx) l2 [ no pm | pm <x> ] [ no tca | tca <x> ]
#       [ no dropped-frames-up | dropped-frames-up <disable|0..4294967295> ] [ no dropped-frames-dn | ... ]
#   configure ethernet ont (uni-idx) l2 pm-collect-ext [ no pm-collect | pm-collect <x> ]
#       [ no p-bits | p-bits <int> ] [ no vlan-id | vlan-id <0..4092> ]
#   configure ethernet ont (uni-idx) cfm [ [ no ] portshut-ais ]
# (path, CLI node, field, CLI name, value regex, device default); defaults ('no <attr>') are not reported.
ETHERNET_ONT_SUBNODE_VALUES = (
    ("phy", "phy", "pm", "pm", r"\S+", "disable"),
    ("l2", "l2", "pm", "pm", r"\S+", "disable"),
    ("l2", "l2", "tca", "tca", r"\S+", "disable"),
    ("l2", "l2", "dropped_frames_up", "dropped-frames-up", r"\S+", "disable"),
    ("l2", "l2", "dropped_frames_dn", "dropped-frames-dn", r"\S+", "disable"),
    ("l2.pm_collect_ext", "l2 pm-collect-ext", "pm_collect", "pm-collect", r"\S+", "disable"),
    ("l2.pm_collect_ext", "l2 pm-collect-ext", "p_bits", "p-bits", r"\d+", 255),
    ("l2.pm_collect_ext", "l2 pm-collect-ext", "vlan_id", "vlan-id", r"\d+", 0),
)
ETHERNET_ONT_SUBNODE_FLAGS = (
    ("cfm", "cfm", "portshut_ais", "portshut-ais"),
)


def _nested(path, leaf):
    """{'l2': {'pm_collect_ext': leaf}} for path 'l2.pm_collect_ext'."""
    for key in reversed(path.split(".")):
        leaf = {key: leaf}
    return leaf


def _subnode_value_parser(path, node, field, cli_name, value_re):
    scope = "configure ethernet ont {{ uni_idx }} " + node + " "
    result = {"uni_idx": "{{ uni_idx }}"}
    result.update(_nested(path, {field: "{{ " + field + " }}"}))
    return {
        "name": "ont." + path + "." + field,
        "compval": path + "." + field,
        "getval": re.compile(
            r"^configure\sethernet\sont\s(?P<uni_idx>\S+)\s" + r"\s".join(re.escape(part) for part in node.split())
            + r"\s" + re.escape(cli_name) + r"\s(?P<" + field + r">" + value_re + r")$"
        ),
        "setval": scope + cli_name + " {{ " + path + "." + field + " }}",
        "remval": scope + "no " + cli_name,
        "result": {"{{ uni_idx }}": result},
    }


def _subnode_flag_parser(path, node, field, cli_name):
    scope = "configure ethernet ont {{ uni_idx }} " + node + " "
    result = {"uni_idx": "{{ uni_idx }}"}
    result.update(_nested(path, {field: True}))
    return {
        "name": "ont." + path + "." + field,
        "compval": path + "." + field,
        "getval": re.compile(
            r"^configure\sethernet\sont\s(?P<uni_idx>\S+)\s" + re.escape(node) + r"\s" + re.escape(cli_name) + r"$"
        ),
        "setval": scope + cli_name,
        "remval": scope + "no " + cli_name,
        "result": {"{{ uni_idx }}": result},
    }


Ethernet_ontsTemplate.PARSERS.extend(
    _subnode_value_parser(path, node, field, cli, value_re)
    for path, node, field, cli, value_re, _default in ETHERNET_ONT_SUBNODE_VALUES
)
Ethernet_ontsTemplate.PARSERS.extend(
    _subnode_flag_parser(path, node, field, cli) for path, node, field, cli in ETHERNET_ONT_SUBNODE_FLAGS
)
