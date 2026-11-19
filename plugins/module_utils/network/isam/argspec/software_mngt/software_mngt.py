# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.software_mngt import (
    SOFTWARE_MNGT_NODES,
    is_int,
)


def _attr_spec(kind, choices):
    if kind == "flag":
        spec = {"type": "bool"}
    elif is_int(kind):
        spec = {"type": "int"}
    else:
        spec = {"type": "str"}
    if choices:
        spec["choices"] = list(choices)
    return spec


def _node_options(node):
    options = {}
    if node["identity"]:
        options[node["identity"]] = {"type": "str", "required": True}
    for option, _cli, kind, _default, choices, _form in node["attrs"]:
        options[option] = _attr_spec(kind, choices)
    return options


def _config_spec():
    spec = {}
    for node in SOFTWARE_MNGT_NODES:
        if node["is_list"]:
            spec[node["key"]] = {"type": "list", "elements": "dict", "options": _node_options(node)}
        else:
            spec[node["key"]] = {"type": "dict", "options": _node_options(node)}
    return spec


class Software_mngtArgs(object):
    """The arg spec for the isam_software_mngt module (generated from SOFTWARE_MNGT_NODES)."""

    argument_spec = {
        "config": {"type": "dict", "options": _config_spec()},
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"],
            "default": "merged",
        },
    }
