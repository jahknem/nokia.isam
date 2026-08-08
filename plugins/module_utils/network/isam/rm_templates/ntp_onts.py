# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
Parser templates for the isam_ntp_onts resource.
"""

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Ntp_ontsTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Ntp_ontsTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "ntp_ont",
            "compval": "ont_id",
            "getval": re.compile(
                r"""
                configure\sntp\sont\s(?P<ont_id>\S+)
                $""", re.VERBOSE),
            "setval": "configure ntp ont {{ ont_id }}",
            "remval": "configure ntp no ont {{ ont_id }}",
            "result": {
                "{{ ont_id }}": {
                    "ont_id": "{{ ont_id }}",
                },
            },
        },
        {
            "name": "ntp_ont.server",
            "compval": "server",
            "getval": re.compile(
                r"""
                configure\sntp\sont\s(?P<ont_id>\S+)\s((?P<negate>no\sserver)|server\s(?P<server>\S+))
                $""", re.VERBOSE),
            "setval": "configure ntp ont {{ ont_id }} {{ 'no server' if server is none else 'server ' + server }}",
            "remval": "configure ntp ont {{ ont_id }} no server",
            "result": {
                "{{ ont_id }}": {
                    "ont_id": "{{ ont_id }}",
                    "server": "{{ '' if negate is defined else server }}",
                },
            },
        },
        {
            "name": "ntp_ont.port",
            "compval": "port",
            "getval": re.compile(
                r"""
                configure\sntp\sont\s(?P<ont_id>\S+)\s((?P<negate>no\sport)|port\s(?P<port>\d+))
                $""", re.VERBOSE),
            "setval": "configure ntp ont {{ ont_id }} {{ 'no port' if port is none else 'port ' + port|string }}",
            "remval": "configure ntp ont {{ ont_id }} no port",
            "result": {
                "{{ ont_id }}": {
                    "ont_id": "{{ ont_id }}",
                    "port": "{{ '' if negate is defined else port|int }}",
                },
            },
        },
        {
            "name": "ntp_ont.poll_interval",
            "compval": "poll_interval",
            "getval": re.compile(
                r"""
                configure\sntp\sont\s(?P<ont_id>\S+)\s((?P<negate>no\spoll-interval)|poll-interval\s(?P<poll_interval>\d+))
                $""", re.VERBOSE),
            "setval": "configure ntp ont {{ ont_id }} {{ 'no poll-interval' if poll_interval is none else 'poll-interval ' + poll_interval|string }}",
            "remval": "configure ntp ont {{ ont_id }} no poll-interval",
            "result": {
                "{{ ont_id }}": {
                    "ont_id": "{{ ont_id }}",
                    "poll_interval": "{{ '' if negate is defined else poll_interval|int }}",
                },
            },
        },
        {
            "name": "ntp_ont.enable",
            "compval": "enable",
            "getval": re.compile(
                r"""
                configure\sntp\sont\s(?P<ont_id>\S+)\s((?P<negate>no\senable)|enable)
                $""", re.VERBOSE),
            "setval": "configure ntp ont {{ ont_id }} {{ 'no enable' if not enable else 'enable' }}",
            "remval": "configure ntp ont {{ ont_id }} no enable",
            "result": {
                "{{ ont_id }}": {
                    "ont_id": "{{ ont_id }}",
                    "enable": "{{ False if negate is defined else True }}",
                },
            },
        },
    ]
    # fmt: on
