# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
Parser templates for the isam_xdsl_lines resource.
"""

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Xdsl_linesTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Xdsl_linesTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "service_profile",
            "getval": re.compile(
                r"""
                configure\sxdsl\sline\s(?P<name>\S+)\sservice-profile\s(?P<service_profile>\S+)
                $""", re.VERBOSE),
            "setval": "configure xdsl line {{ name }} service-profile {{ service_profile }}",
            "result": {
                "{{ name }}": {
                    "name": "{{ name }}",
                    "service_profile": "{{ service_profile }}",
                }
            },
        },
        {
            "name": "spectrum_profile",
            "getval": re.compile(
                r"""
                configure\sxdsl\sline\s(?P<name>\S+)\sspectrum-profile\s(?P<spectrum_profile>\S+)
                $""", re.VERBOSE),
            "setval": "configure xdsl line {{ name }} spectrum-profile {{ spectrum_profile }}",
            "result": {
                "{{ name }}": {
                    "name": "{{ name }}",
                    "spectrum_profile": "{{ spectrum_profile }}",
                }
            },
        },
        {
            "name": "dpbo_profile",
            "getval": re.compile(
                r"""
                configure\sxdsl\sline\s(?P<name>\S+)\sdpbo-profile\s(?P<dpbo_profile>\S+)
                $""", re.VERBOSE),
            "setval": "configure xdsl line {{ name }} dpbo-profile {{ dpbo_profile }}",
            "result": {
                "{{ name }}": {
                    "name": "{{ name }}",
                    "dpbo_profile": "{{ dpbo_profile }}",
                }
            },
        },
        {
            "name": "vect_profile",
            "getval": re.compile(
                r"""
                configure\sxdsl\sline\s(?P<name>\S+)\svect-profile\s(?P<vect_profile>\S+)
                $""", re.VERBOSE),
            "setval": "configure xdsl line {{ name }} vect-profile {{ vect_profile }}",
            "result": {
                "{{ name }}": {
                    "name": "{{ name }}",
                    "vect_profile": "{{ vect_profile }}",
                }
            },
        },
        {
            "name": "admin_up",
            "getval": re.compile(
                r"""
                configure\sxdsl\sline\s(?P<name>\S+)\s((?P<negate_admin_up>no\sadmin-up)|(?P<admin_up>admin-up))
                $""", re.VERBOSE),
            "setval": "configure xdsl line {{ name }} {{ 'no ' if admin_up == false else '' }}admin-up",
            "result": {
                "{{ name }}": {
                    "name": "{{ name }}",
                    "admin_up": "{{ False if negate_admin_up is defined else True }}",
                }
            },
        },
    ]
    # fmt: on
