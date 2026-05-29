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
