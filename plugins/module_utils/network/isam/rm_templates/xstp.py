# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class XstpTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(XstpTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "general.enable_stp",
            "getval": re.compile(
                r"""
                ^configure\sxstp\sgeneral\s(?P<negate_enable_stp>no\senable-stp|enable-stp)
                $""", re.VERBOSE),
            "setval": "configure xstp general {{ 'no ' if general.enable_stp == false else '' }}enable-stp",
            "result": {
                "general": {
                    "enable_stp": "{{ False if negate_enable_stp == 'no enable-stp' else True }}",
                },
            },
        },
        {
            "name": "general.region_name",
            "getval": re.compile(
                r"""
                ^configure\sxstp\sgeneral\sregion-name\s(?P<region_name>.+?)
                $""", re.VERBOSE),
            "setval": "configure xstp general region-name {{ general.region_name }}",
            "result": {
                "general": {
                    "region_name": "{{ region_name }}",
                },
            },
        },
        {
            "name": "ports.path_cost",
            "getval": re.compile(
                r"""
                ^configure\sxstp\sport\s(?P<port>\S+)\spath-cost\s(?P<path_cost>\d+)
                $""", re.VERBOSE),
            "setval": "configure xstp port {{ port }} path-cost {{ path_cost }}",
            "result": {
                "ports": {
                    "{{ port }}": {
                        "port": "{{ port }}",
                        "path_cost": "{{ path_cost|int }}",
                    },
                },
            },
        },
    ]
    # fmt: on


# Attributes with a 'no <attr>' reset form (CLI reference, MSTP general/port configuration).
# value: (CLI name, device default, type); flags have default False.
XSTP_GENERAL_FIELDS = {
    "priority": ("priority", 32768, int),
    "max_instance_num": ("max-instance-num", 65, int),
    "max_age": ("max-age", 2000, int),
    "hello_time": ("hello-time", 200, int),
    "forward_delay": ("forward-delay", 1500, int),
    "version": ("version", "mstp", str),
    "tx_hold_count": ("tx-hold-count", 3, int),
    "path_cost_type": ("path-cost-type", "32-bit", str),
    "max_hop_count": ("max-hop-count", 2000, int),
    "region_version": ("region-version", 0, int),
    "config_id_sel": ("config-id-sel", 0, int),
}
XSTP_PORT_FIELDS = {
    "priority": ("priority", 128, int),
    "admin_p2p": ("admin-p2p", "auto", str),
    "hello_time": ("hello-time", 200, int),
}
XSTP_PORT_FLAGS = {
    "enable_stp": "enable-stp",
    "edge_port": "edge-port",
}


def _general_value_parser(field, cli_name):
    return {
        "name": "general." + field,
        "getval": re.compile(r"^configure\s+xstp\s+general\s+" + re.escape(cli_name) + r"\s+(?P<" + field + r">\S+)$"),
        "setval": "configure xstp general " + cli_name + " {{ general." + field + " }}",
        "remval": "configure xstp general no " + cli_name,
        "result": {"general": {field: "{{ " + field + " }}"}},
    }


def _port_value_parser(field, cli_name):
    return {
        "name": "ports." + field,
        "getval": re.compile(
            r"^configure\s+xstp\s+port\s+(?P<port>\S+)\s+" + re.escape(cli_name) + r"\s+(?P<" + field + r">\S+)$"
        ),
        "setval": "configure xstp port {{ port }} " + cli_name + " {{ " + field + " }}",
        "remval": "configure xstp port {{ port }} no " + cli_name,
        "result": {"ports": {"{{ port }}": {"port": "{{ port }}", field: "{{ " + field + " }}"}}},
    }


def _port_flag_parser(field, cli_name):
    return {
        "name": "ports." + field,
        "getval": re.compile(r"^configure\s+xstp\s+port\s+(?P<port>\S+)\s+" + re.escape(cli_name) + r"$"),
        "setval": "configure xstp port {{ port }} " + cli_name,
        "remval": "configure xstp port {{ port }} no " + cli_name,
        "result": {"ports": {"{{ port }}": {"port": "{{ port }}", field: True}}},
    }


XstpTemplate.PARSERS.extend(_general_value_parser(f, spec[0]) for f, spec in XSTP_GENERAL_FIELDS.items())
XstpTemplate.PARSERS.extend(_port_value_parser(f, spec[0]) for f, spec in XSTP_PORT_FIELDS.items())
XstpTemplate.PARSERS.extend(_port_flag_parser(f, cli) for f, cli in XSTP_PORT_FLAGS.items())
