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
            "name": "rtx_profile",
            "getval": re.compile(r"^configure\sxdsl\sline\s(?P<name>\S+)\srtx-profile\s(?P<rtx_profile>\S+)$"),
            "setval": "configure xdsl line {{ name }} rtx-profile {{ rtx_profile }}",
            "remval": "configure xdsl line {{ name }} no rtx-profile",
            "result": {"{{ name }}": {"name": "{{ name }}", "rtx_profile": "{{ rtx_profile }}"}},
        },
        {
            "name": "sos_profile",
            "getval": re.compile(r"^configure\sxdsl\sline\s(?P<name>\S+)\ssos-profile\s(?P<sos_profile>\S+)$"),
            "setval": "configure xdsl line {{ name }} sos-profile {{ sos_profile }}",
            "remval": "configure xdsl line {{ name }} no sos-profile",
            "result": {"{{ name }}": {"name": "{{ name }}", "sos_profile": "{{ sos_profile }}"}},
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


for _field, _cli_name in (
    ("service_profile", "service-profile"),
    ("spectrum_profile", "spectrum-profile"),
    ("dpbo_profile", "dpbo-profile"),
    ("vect_profile", "vect-profile"),
    ("rtx_profile", "rtx-profile"),
    ("sos_profile", "sos-profile"),
):
    for _parser in Xdsl_linesTemplate.PARSERS:
        if _parser["name"] != _field:
            continue
        _parser["getval"] = re.compile(
            r"^configure\s+xdsl\s+line\s+(?P<name>\S+)\s+(?:(?P<negate>no\s+"
            + re.escape(_cli_name)
            + r")|"
            + re.escape(_cli_name)
            + r"\s+(?P<"
            + _field
            + r">\S+))$"
        )
        _parser["setval"] = (
            "configure xdsl line {{ name }} {{ 'no "
            + _cli_name
            + "' if "
            + _field
            + " is none else '"
            + _cli_name
            + " ' + "
            + _field
            + " }}"
        )
        _parser["remval"] = "configure xdsl line {{ name }} no " + _cli_name
        _parser["result"] = {
            "{{ name }}": {
                "name": "{{ name }}",
                _field: "{{ '' if negate is defined else " + _field + " }}",
            }
        }
        break


def _xdsl_value_parser(field, cli_name):
    return {
        "name": field,
        "getval": re.compile(
            r"^configure\s+xdsl\s+line\s+(?P<name>\S+)\s+(?:(?P<negate>no\s+"
            + re.escape(cli_name)
            + r")|"
            + re.escape(cli_name)
            + r"\s+(?P<"
            + field
            + r">\S+))$"
        ),
        "setval": (
            "configure xdsl line {{ name }} {{ 'no "
            + cli_name
            + "' if "
            + field
            + " is none else '"
            + cli_name
            + " ' + "
            + field
            + " }}"
        ),
        "remval": "configure xdsl line {{ name }} no " + cli_name,
        "result": {"{{ name }}": {"name": "{{ name }}", field: "{{ '' if negate is defined else " + field + " }}"}},
    }


def _xdsl_flag_parser(field, cli_name):
    return {
        "name": field,
        "getval": re.compile(
            r"^configure\s+xdsl\s+line\s+(?P<name>\S+)\s+(?:(?P<negate>no\s+)?"
            + re.escape(cli_name)
            + r")$"
        ),
        "setval": (
            "configure xdsl line {{ name }} {{ '"
            + cli_name
            + "' if "
            + field
            + " else 'no "
            + cli_name
            + "' }}"
        ),
        "remval": "configure xdsl line {{ name }} no " + cli_name,
        "result": {"{{ name }}": {"name": "{{ name }}", field: "{{ negate is not defined }}"}},
    }


Xdsl_linesTemplate.PARSERS.extend(
    [
        _xdsl_value_parser("carrier_data_mode", "carrier-data-mode"),
        _xdsl_value_parser("transfer_mode", "transfer-mode"),
        _xdsl_value_parser("vect_qln_mode", "vect-qln-mode"),
        _xdsl_value_parser("vect_fallback", "vect-fallback"),
    ]
    + [
        _xdsl_flag_parser(field, cli_name)
        for field, cli_name in (
            ("ansi_t1413", "ansi-t1413"),
            ("etsi_dts", "etsi-dts"),
            ("g992_1_a", "g992-1-a"),
            ("g992_1_b", "g992-1-b"),
            ("g992_2_a", "g992-2-a"),
            ("g992_3_a", "g992-3-a"),
            ("g992_3_b", "g992-3-b"),
            ("g992_3_aj", "g992-3-aj"),
            ("g992_3_l1", "g992-3-l1"),
            ("g992_3_l2", "g992-3-l2"),
            ("g992_3_am", "g992-3-am"),
            ("g992_5_a", "g992-5-a"),
            ("g992_5_b", "g992-5-b"),
            ("ansi_t1_424", "ansi-t1.424"),
            ("etsi_ts", "etsi-ts"),
            ("itu_g993_1", "itu-g993-1"),
            ("ieee_802_3ah", "ieee-802.3ah"),
            ("g992_5_aj", "g992-5-aj"),
            ("g992_5_am", "g992-5-am"),
            ("g993_2_8a", "g993-2-8a"),
            ("g993_2_8b", "g993-2-8b"),
            ("g993_2_8c", "g993-2-8c"),
            ("g993_2_8d", "g993-2-8d"),
            ("g993_2_12a", "g993-2-12a"),
            ("g993_2_12b", "g993-2-12b"),
            ("g993_2_17a", "g993-2-17a"),
            ("g993_2_30a", "g993-2-30a"),
            ("g993_2_35b", "g993-2-35b"),
            ("imp_noise_sensor", "imp-noise-sensor"),
            ("auto_switch", "auto-switch"),
        )
    ]
)
