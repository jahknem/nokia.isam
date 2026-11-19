# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
Parser templates for the isam_generic_pon resource (global PON settings).

The device prints each node as one packed line ('flat detail', lab ISAM)::

    configure generic-pon dpinteg-threshold 0
    configure generic-pon utilization no pon-pmcollect no ont-pmcollect
    configure generic-pon utilization threshold no txmcutilhi ... no dbacongthresh
    configure generic-pon ont no slid-mode no sn-bundle-timer no sw-ver-mis-block no sn-autounlock
    configure generic-pon alarmflag no ponlos-alarm-ctrl

GENERIC_PON_NODES is the single description of that grammar (from the CLI guide): the
facts split packed lines with it, the parsers are generated from it, the config class
takes the device defaults from it. Every attribute is "[ no kw | kw <value> ]".
"""

import re

from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import remove_empties

_THRESHOLDS = (
    "txmcutilhi", "txmcutilmd", "txmcutillo", "txtotutilhi", "txtotutilmd", "txtotutillo",
    "rxtotutilhi", "rxtotutilmd", "rxtotutillo", "dbacongperiodhi", "dbacongperiodmd", "dbacongperiodlo",
    "txucdropfrmhi", "txucdropfrmmd", "txucdropfrmlo", "txmcdropfrmhi", "txmcdropfrmmd", "txmcdropfrmlo",
    "txbcdropfrmhi", "txbcdropfrmmd", "txbcdropfrmlo", "rxtotdropfrmhi", "rxtotdropfrmmd", "rxtotdropfrmlo",
    "numtcint", "numtcintdba", "dbacongthresh",
)

# (path in the config, CLI node after "configure generic-pon", attributes); an attribute
# is (option, CLI keyword, kind "value"|"int", device default).
GENERIC_PON_NODES = (
    (("utilization",), "utilization", (
        ("pon_pmcollect", "pon-pmcollect", "value", "none"),
        ("ont_pmcollect", "ont-pmcollect", "value", "disable"),
    )),
    (("utilization", "threshold"), "utilization threshold",
     tuple((name, name, "value", "disabled") for name in _THRESHOLDS)),
    (("ont",), "ont", (
        ("slid_mode", "slid-mode", "value", "ascii"),
        ("sn_bundle_timer", "sn-bundle-timer", "int", 24),
        ("sw_ver_mis_block", "sw-ver-mis-block", "value", "enable"),
        ("sn_autounlock", "sn-autounlock", "value", "disable"),
    )),
    (("alarmflag",), "alarmflag", (
        ("ponlos_alarm_ctrl", "ponlos-alarm-ctrl", "value", "disable"),
    )),
)


def section(config, path):
    """The settings dict at path ({} when absent)."""
    for key in path:
        config = config.get(key) if isinstance(config, dict) else None
    return config if isinstance(config, dict) else {}


def without_defaults(config):
    """A copy of config without values equal to their device default (defaults count as unset)."""
    config = deepcopy(config or {})
    for path, _node, attrs in GENERIC_PON_NODES:
        values = section(config, path)
        for option, _cli, _kind, default in attrs:
            if option in values and values[option] == default:
                del values[option]
    return remove_empties(config)


def parser_name(path, option):
    return ".".join(path + (option,))


def _nested(path, leaf):
    for key in reversed(path):
        leaf = {key: leaf}
    return leaf


def _attribute_parser(path, node, option, cli, kind):
    scope = "configure generic-pon " + node
    words = r"\s".join(re.escape(word) for word in node.split())
    return {
        "name": parser_name(path, option),
        "compval": option,
        "getval": re.compile(r"^configure\sgeneric-pon\s" + words + r"\s(?:(?P<negate>no\s)" + re.escape(cli)
                             + r"|" + re.escape(cli) + r"\s(?P<value>\S+))$"),
        "setval": scope + " " + cli + " {{ " + option + " }}",
        "remval": scope + " no " + cli,
        "result": _nested(path, {option: "{{ none if negate is defined else value" + ("|int" if kind == "int" else "") + " }}"}),
    }


PARSERS = [{
    # mandatory value without removal form (CLI guide); the device prints it also at 0
    "name": "dpinteg_threshold",
    "compval": "dpinteg_threshold",
    "getval": re.compile(r"^configure\sgeneric-pon\sdpinteg-threshold\s(?P<value>\d+)$"),
    "setval": "configure generic-pon dpinteg-threshold {{ dpinteg_threshold }}",
    "no_remval": True,
    "result": {"dpinteg_threshold": "{{ value|int }}"},
}]
for _path, _node, _attrs in GENERIC_PON_NODES:
    PARSERS.extend(_attribute_parser(_path, _node, option, cli, kind) for option, cli, kind, _default in _attrs)


class Generic_ponTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Generic_ponTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    PARSERS = PARSERS
