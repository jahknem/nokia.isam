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
            "result": {
                "{{ uni_idx }}": {
                    "uni_idx": "{{ uni_idx }}",
                    "admin_state": "{{ admin_state }}",
                }
            },
        },
    ]
    # fmt: on
