# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Pon_interfacesTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Pon_interfacesTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "interface.label",
            "compval": "label",
            "getval": re.compile(
                r"""
                configure\spon\sinterface\s(?P<name>\S+)\s((?P<negate>no\slabel)|label\s(?P<label>.+))
                $""", re.VERBOSE),
            "setval": "configure pon interface {{ name }} {{ 'no label' if label is none else 'label ' + label }}",
            "remval": "configure pon interface {{ name }} no label",
            "result": {
                "{{ name }}": {
                    "name": "{{ name }}",
                    "label": "{{ '' if negate is defined else label }}",
                },
            },
        },
        {
            "name": "interface.fec_dn",
            "compval": "fec_dn",
            "getval": re.compile(
                r"""
                configure\spon\sinterface\s(?P<name>\S+)\s((?P<negate>no\sfec-dn)|fec-dn\s(?P<fec_dn>\S+))
                $""", re.VERBOSE),
            "setval": "configure pon interface {{ name }} {{ 'no fec-dn' if fec_dn is none else 'fec-dn ' + fec_dn }}",
            "remval": "configure pon interface {{ name }} no fec-dn",
            "result": {
                "{{ name }}": {
                    "name": "{{ name }}",
                    "fec_dn": "{{ 'disable' if negate is defined else fec_dn }}",
                },
            },
        },
        {
            "name": "interface.ponid_interval",
            "compval": "ponid_interval",
            "getval": re.compile(
                r"""
                configure\spon\sinterface\s(?P<name>\S+)\s((?P<negate>no\sponid-interval)|ponid-interval\s(?P<ponid_interval>\d+))
                $""", re.VERBOSE),
            "setval": "configure pon interface {{ name }} {{ 'no ponid-interval' if ponid_interval is none else 'ponid-interval ' + ponid_interval|string }}",
            "remval": "configure pon interface {{ name }} no ponid-interval",
            "result": {
                "{{ name }}": {
                    "name": "{{ name }}",
                    "ponid_interval": "{{ 0 if negate is defined else ponid_interval }}",
                },
            },
        },
        {
            "name": "interface.ponid_identifier",
            "compval": "ponid_identifier",
            "getval": re.compile(
                r"""
                configure\spon\sinterface\s(?P<name>\S+)\s((?P<negate>no\sponid-identifier)|ponid-identifier\s(?P<ponid_identifier>\S+))
                $""", re.VERBOSE),
            "setval": "configure pon interface {{ name }} {{ 'no ponid-identifier' if ponid_identifier is none else 'ponid-identifier ' + ponid_identifier }}",
            "remval": "configure pon interface {{ name }} no ponid-identifier",
            "result": {
                "{{ name }}": {
                    "name": "{{ name }}",
                    "ponid_identifier": "{{ '00000000000000' if negate is defined else ponid_identifier }}",
                },
            },
        },
        {
            "name": "interface.tconts_per_frame",
            "compval": "tconts_per_frame",
            "getval": re.compile(
                r"""
                configure\spon\sinterface\s(?P<name>\S+)\s((?P<negate>no\stconts-per-frame)|tconts-per-frame\s(?P<tconts_per_frame>\d+))
                $""", re.VERBOSE),
            "setval": "configure pon interface {{ name }} {{ 'no tconts-per-frame' if tconts_per_frame is none else 'tconts-per-frame ' + tconts_per_frame|string }}",
            "remval": "configure pon interface {{ name }} no tconts-per-frame",
            "result": {
                "{{ name }}": {
                    "name": "{{ name }}",
                    "tconts_per_frame": "{{ 64 if negate is defined else tconts_per_frame }}",
                },
            },
        },
        {
            "name": "interface.admin_state",
            "compval": "admin_state",
            "getval": re.compile(
                r"""
                configure\spon\sinterface\s(?P<name>\S+)\s((?P<negate>no\sadmin-state)|admin-state\s(?P<admin_state>\S+))
                $""", re.VERBOSE),
            "setval": "configure pon interface {{ name }} {{ 'no admin-state' if admin_state is none else 'admin-state ' + admin_state }}",
            "remval": "configure pon interface {{ name }} no admin-state",
            "result": {
                "{{ name }}": {
                    "name": "{{ name }}",
                    "admin_state": "{{ 'down' if negate is defined else admin_state }}",
                },
            },
        },
        {
            "name": "interface.tc_layer.pm_collect",
            "compval": "tc_layer.pm_collect",
            "getval": re.compile(
                r"""
                configure\spon\sinterface\s(?P<name>\S+)\stc-layer\s((?P<negate>no\spm-collect)|pm-collect\s(?P<pm_collect>\S+))
                $""", re.VERBOSE),
            "setval": "configure pon interface {{ name }} tc-layer {{ 'no pm-collect' if tc_layer.pm_collect is none else 'pm-collect ' + tc_layer.pm_collect }}",
            "remval": "configure pon interface {{ name }} tc-layer no pm-collect",
            "result": {
                "{{ name }}": {
                    "name": "{{ name }}",
                    "tc_layer": {
                        "pm_collect": "{{ 'pm-enable' if negate is defined else pm_collect }}",
                        "tca_enable": "{{ True if pm_collect == 'tca-enable' else False }}",
                    },
                },
            },
        },
        {
            "name": "interface.tc_layer.tca_enable",
            "compval": "tc_layer.tca_enable",
            "getval": re.compile(
                r"""
                configure\spon\sinterface\s(?P<name>\S+)\stc-layer\spm-collect\s(?P<pm_collect>\S+)
                $""", re.VERBOSE),
            "setval": "configure pon interface {{ name }} tc-layer pm-collect {{ 'tca-enable' if tc_layer.tca_enable else 'pm-enable' }}",
            "remval": "configure pon interface {{ name }} tc-layer no pm-collect",
            "result": {
                "{{ name }}": {
                    "name": "{{ name }}",
                    "tc_layer": {
                        "tca_enable": "{{ True if pm_collect == 'tca-enable' else False }}",
                    },
                },
            },
        },
    ]
    # fmt: on
