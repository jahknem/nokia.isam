# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Link_aggTemplate(NetworkTemplate):
    """Parser templates for configure link-agg port and group."""

    def __init__(self, lines=None, module=None):
        super(Link_aggTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "port.passive_lacp",
            "getval": re.compile(
                r"""configure\slink-agg\sport\s(?P<id>\S+)\s(?P<negate>no\s)?passive-lacp$""",
                re.VERBOSE,
            ),
            "setval": "configure link-agg port {{ id }} {{ 'no ' if not passive_lacp else '' }}passive-lacp",
            "result": {
                "port_{{ id }}": {
                    "type": "port",
                    "id": "{{ id }}",
                    "passive_lacp": "{{ False if negate is defined else True }}",
                },
            },
        },
        {
            "name": "port.short_timeout",
            "getval": re.compile(
                r"""configure\slink-agg\sport\s(?P<id>\S+)\s(?P<negate>no\s)?short-timeout$""",
                re.VERBOSE,
            ),
            "setval": "configure link-agg port {{ id }} {{ 'no ' if not short_timeout else '' }}short-timeout",
            "result": {
                "port_{{ id }}": {
                    "type": "port",
                    "id": "{{ id }}",
                    "short_timeout": "{{ False if negate is defined else True }}",
                },
            },
        },
        {
            "name": "port.actor_port_prio",
            "getval": re.compile(
                r"""configure\slink-agg\sport\s(?P<id>\S+)\s(?:(?P<negate>no\sactor-port-prio)|actor-port-prio\s(?P<actor_port_prio>\d+))$""",
                re.VERBOSE,
            ),
            "setval": "configure link-agg port {{ id }} actor-port-prio {{ actor_port_prio }}",
            "result": {
                "port_{{ id }}": {
                    "type": "port",
                    "id": "{{ id }}",
                    "actor_port_prio": "{{ '1' if negate is defined else actor_port_prio }}",
                },
            },
        },
        {
            "name": "group.load_sharing_policy",
            "getval": re.compile(
                r"""configure\slink-agg\sgroup\s(?P<id>\S+)\sload-sharing-policy\s(?P<load_sharing_policy>\S+)$""",
                re.VERBOSE,
            ),
            "setval": "configure link-agg group {{ id }} load-sharing-policy {{ load_sharing_policy }}",
            "result": {
                "group_{{ id }}": {
                    "type": "group",
                    "id": "{{ id }}",
                    "load_sharing_policy": "{{ load_sharing_policy }}",
                },
            },
        },
        {
            "name": "group.max_active_port",
            "getval": re.compile(
                r"""configure\slink-agg\sgroup\s(?P<id>\S+)\s(?:(?P<negate>no\smax-active-port)|max-active-port\s(?P<max_active_port>\d+))$""",
                re.VERBOSE,
            ),
            "setval": "configure link-agg group {{ id }} max-active-port {{ max_active_port }}",
            "result": {
                "group_{{ id }}": {
                    "type": "group",
                    "id": "{{ id }}",
                    "max_active_port": "{{ '8' if negate is defined else max_active_port }}",
                },
            },
        },
        {
            "name": "group.swo_threshold",
            "getval": re.compile(
                r"""configure\slink-agg\sgroup\s(?P<id>\S+)\s(?:(?P<negate>no\sswo-threshold)|swo-threshold\s(?P<swo_threshold>\d+))$""",
                re.VERBOSE,
            ),
            "setval": "configure link-agg group {{ id }} swo-threshold {{ swo_threshold }}",
            "result": {
                "group_{{ id }}": {
                    "type": "group",
                    "id": "{{ id }}",
                    "swo_threshold": "{{ '0' if negate is defined else swo_threshold }}",
                },
            },
        },
        {
            "name": "group.priority",
            "getval": re.compile(
                r"""configure\slink-agg\sgroup\s(?P<id>\S+)\s(?:(?P<negate>no\spriority)|priority\s(?P<priority>\d+))$""",
                re.VERBOSE,
            ),
            "setval": "configure link-agg group {{ id }} priority {{ priority }}",
            "result": {
                "group_{{ id }}": {
                    "type": "group",
                    "id": "{{ id }}",
                    "priority": "{{ '0' if negate is defined else priority }}",
                },
            },
        },
        {
            "name": "group.swo_revert",
            "getval": re.compile(
                r"""configure\slink-agg\sgroup\s(?P<id>\S+)\sswo-revert\s(?P<swo_revert>\S+)$""",
                re.VERBOSE,
            ),
            "setval": "configure link-agg group {{ id }} swo-revert {{ swo_revert }}",
            "result": {
                "group_{{ id }}": {
                    "type": "group",
                    "id": "{{ id }}",
                    "swo_revert": "{{ swo_revert }}",
                },
            },
        },
        {
            "name": "group.mode",
            "getval": re.compile(
                r"""configure\slink-agg\sgroup\s(?P<id>\S+)\smode\s(?P<mode>\S+)$""",
                re.VERBOSE,
            ),
            "setval": "configure link-agg group {{ id }} mode {{ mode }}",
            "result": {
                "group_{{ id }}": {
                    "type": "group",
                    "id": "{{ id }}",
                    "mode": "{{ mode }}",
                },
            },
        },
        {
            "name": "group.master_iwf",
            "getval": re.compile(
                r"""configure\slink-agg\sgroup\s(?P<id>\S+)\smaster-iwf\s(?P<master_iwf>\S+)$""",
                re.VERBOSE,
            ),
            "setval": "configure link-agg group {{ id }} master-iwf {{ master_iwf }}",
            "result": {
                "group_{{ id }}": {
                    "type": "group",
                    "id": "{{ id }}",
                    "master_iwf": "{{ master_iwf }}",
                },
            },
        },
        {
            "name": "group.port",
            "getval": re.compile(
                r"""configure\slink-agg\sgroup\s(?P<id>\S+)\s(?P<negate>no\s)?port\s(?P<port>\S+)$""",
                re.VERBOSE,
            ),
            "setval": "configure link-agg group {{ id }} port {{ port }}",
            "result": {
                "group_{{ id }}": {
                    "type": "group",
                    "id": "{{ id }}",
                    "ports": {
                        "{{ port }}": "{{ port }}",
                    },
                },
            },
        },
    ]
    # fmt: on
