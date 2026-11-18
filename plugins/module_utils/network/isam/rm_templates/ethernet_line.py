# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
Parser templates for the isam_ethernet_line resource.

The device prints all attributes of a node on one line (lab ISAM)::

    configure ethernet line 1/1/6/1 port-type uni no admin-up
    configure ethernet line 1/1/6/1 tca-line-threshold no enable no los ... no tx-octets-day
    configure ethernet line 1/1/6/1 mau 1 type 100basebx10d power down no speed-auto-sense ...

The facts split such lines into one attribute per line (iter_cli_fields); each parser
below reads and writes one attribute, and COMPACT_COMMAND_SCOPES (config class) packs
the commands of one node again.
"""

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)

LINE = r"^configure\sethernet\sline\s(?P<if_index>\S+)\s"
MAU = LINE + r"mau\s(?P<index>\d+)\s"
TCA = LINE + r"tca-line-threshold\s"

# CLI keywords per node; the flattening in the facts and the parsers both use them.
LINE_FLAGS = ("admin-up",)
LINE_VALUES = ("port-type",)
TCA_FLAGS = ("enable",)
TCA_THRESHOLDS = ("los", "fcs", "rx-octets", "tx-octets", "los-day", "fcs-day", "rx-octets-day", "tx-octets-day")
MAU_FLAGS = ("speed-auto-sense", "autonegotiate", "cap100base-tfd", "cap1000base-xfd", "cap1000base-tfd")
MAU_VALUES = ("type", "power")


def _key(cli):
    return cli.replace("-", "_")


def _flag(name, getval_prefix, scope, cli, key, result):
    """[no] <cli>: True / False."""
    return {
        "name": name,
        "getval": re.compile(getval_prefix + r"(?P<negate>no\s)?" + re.escape(cli) + r"$"),
        "setval": scope + " " + cli,
        "remval": scope + " no " + cli,
        "result": result("{{ False if negate is defined else True }}"),
        "compval": key,
    }


def _value(name, getval_prefix, scope, cli, key, result, kind="str", removable=True):
    """<cli> <value> / no <cli> (unset, the device default)."""
    parser = {
        "name": name,
        "getval": re.compile(getval_prefix + r"(?:(?P<negate>no\s)" + re.escape(cli) + r"|" + re.escape(cli)
                             + r"\s(?P<value>\S+))$"),
        "setval": scope + " " + cli + " {{ " + key + " }}",
        "result": result("{{ none if negate is defined else value" + ("|int" if kind == "int" else "") + " }}"),
        "compval": key,
    }
    if removable:
        parser["remval"] = scope + " no " + cli
    else:
        parser["no_remval"] = True  # set only: the CLI has no "no" form
    return parser


def _line_result(key):
    return lambda value: {"{{ if_index }}": {"if_index": "{{ if_index }}", key: value}}


def _tca_result(key):
    return lambda value: {"{{ if_index }}": {"if_index": "{{ if_index }}", "tca_line_threshold": {key: value}}}


def _mau_result(key):
    return lambda value: {"{{ if_index }}": {"if_index": "{{ if_index }}",
                                             "mau": {"{{ index }}": {"index": "{{ index|int }}", key: value}}}}


LINE_SCOPE = "configure ethernet line {{ if_index }}"
TCA_SCOPE = LINE_SCOPE + " tca-line-threshold"
MAU_SCOPE = LINE_SCOPE + " mau {{ index }}"

LINE_PARSERS = (
    [_value(_key(cli), LINE, LINE_SCOPE, cli, _key(cli), _line_result(_key(cli)), removable=False) for cli in LINE_VALUES]
    + [_flag(_key(cli), LINE, LINE_SCOPE, cli, _key(cli), _line_result(_key(cli))) for cli in LINE_FLAGS]
)
TCA_PARSERS = (
    [_flag("tca_line_threshold." + _key(cli), TCA, TCA_SCOPE, cli, "tca_line_threshold." + _key(cli),
           _tca_result(_key(cli))) for cli in TCA_FLAGS]
    + [_value("tca_line_threshold." + _key(cli), TCA, TCA_SCOPE, cli, "tca_line_threshold." + _key(cli),
              _tca_result(_key(cli)), kind="int") for cli in TCA_THRESHOLDS]
)
MAU_PARSERS = (
    [_value("mau.mau_type", MAU, MAU_SCOPE, "type", "mau_type", _mau_result("mau_type"), removable=False),
     _value("mau.power", MAU, MAU_SCOPE, "power", "power", _mau_result("power"), removable=False)]
    + [_flag("mau." + _key(cli), MAU, MAU_SCOPE, cli, _key(cli), _mau_result(_key(cli))) for cli in MAU_FLAGS]
)


class Ethernet_lineTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Ethernet_lineTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    PARSERS = LINE_PARSERS + TCA_PARSERS + MAU_PARSERS
