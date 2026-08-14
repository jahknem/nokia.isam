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
                    "fec_dn": "{{ ('enable' if (name.startswith('x-pon:') or name.startswith('25g-pon:')) else 'disable') if negate is defined else fec_dn }}",
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
                    "ponid_identifier": "{{ ('x00000000000000')[1:] if negate is defined else ponid_identifier }}",
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
                    "tconts_per_frame": "{{ (44 if (name.startswith('x-pon:') or name.startswith('25g-pon:')) else 64) if negate is defined else tconts_per_frame }}",
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


def _value_parser(field, cli_name, value_pattern=r"\S+", value_filter="", default_value="''"):
    """Build a parser for one packed PON-interface command word."""
    value = "{{ " + default_value + value_filter + " if negate is defined else " + field + value_filter + " }}"
    return {
        "name": "interface." + field,
        "compval": field,
        "getval": re.compile(
            r"^configure\spon\sinterface\s(?P<name>\S+)\s"
            r"(?:(?P<negate>no\s+)" + re.escape(cli_name) + r"|"
            + re.escape(cli_name) + r"\s+(?P<" + field + r">" + value_pattern + r"))$"
        ),
        "setval": "configure pon interface {{ name }} {{ 'no " + cli_name
        + "' if " + field + " is none else '" + cli_name + " ' + " + field + "|string }}",
        "remval": "configure pon interface {{ name }} no " + cli_name,
        "result": {
            "{{ name }}": {
                "name": "{{ name }}",
                field: value,
            }
        },
    }


Pon_interfacesTemplate.PARSERS.extend(
    [
        _value_parser("ber_calc_period", "ber-calc-period", r"\d+", "|int", "10"),
        _value_parser("polling_period", "polling-period", r"\d+", "|int", "100"),
        _value_parser("sig_degrade_th", "sig-degrade-th", r"\d+", "|int", "9"),
        _value_parser("sig_fail_th", "sig-fail-th", r"\d+", "|int", "5"),
        _value_parser("raman_reduct", "raman-reduct", r"\S+", "", "'disable'"),
        _value_parser("closest_ont", "closest-ont", r"\d+", "|int", "0"),
        _value_parser("diff_reach", "diff-reach", r"\d+", "|int", "20"),
        _value_parser("pon_tag", "pon-tag", r"\S+", "", "('x0000000000000000')[1:]"),
        _value_parser("pon_id", "pon-id", r"\S+", "", "('x00000000')[1:]"),
        _value_parser("mcast_encrypt", "mcast-encrypt", r"\S+", "", "'disable'"),
        _value_parser("auth_method", "auth-method", r"\S+", "", "'sn-slid'"),
        _value_parser("ponid_odn", "ponid-odn", r"\S+", "", "'auto'"),
        _value_parser("max_ranging_onts", "max-ranging-onts", r"\d+", "|int", "128"),
        _value_parser("pon_speed", "pon-speed", r"\S+", "", "'nominal'"),
        _value_parser("burst_overhead", "burst-overhead", r"\S+", "", "'robust'"),
        _value_parser("onu_prov_mode", "onu-prov-mode", r"\S+", "", "'semi-auto'"),
    ]
)


def _nested_value_parser(section, field, cli_path, value_pattern=r"\S+", value_filter=""):
    """Build a parser for a documented nested PON-interface branch."""
    parent_path, cli_name = cli_path.rsplit(" ", 1)
    value = "{{ '' if negate is defined else value" + value_filter + " }}"
    result = {"name": "{{ name }}"}
    target = result
    for part in section.split("."):
        target[part] = {}
        target = target[part]
    target[field] = value
    return {
        "name": "interface.%s.%s" % (section, field),
        "compval": "%s.%s" % (section, field),
        "getval": re.compile(
            r"^configure\spon\sinterface\s(?P<name>\S+)\s"
            r"%s\s(?:(?P<negate>no\s+)%s|%s\s+(?P<value>%s))$"
            % (
                r"\s+".join(re.escape(part) for part in parent_path.split()),
                re.escape(cli_name),
                re.escape(cli_name),
                value_pattern,
            )
        ),
        "setval": "configure pon interface {{ name }} %s {{ 'no %s' if %s.%s is none else '%s ' + %s.%s|string }}"
        % (parent_path, cli_name, section, field, cli_name, section, field),
        "remval": "configure pon interface {{ name }} %s no %s" % (parent_path, cli_name),
        "result": {"{{ name }}": result},
    }


def _nested_flag_parser(section, cli_path, choices, field="pm_collect"):
    """Build a parser for a nested enumerated PON-interface setting."""
    return _nested_value_parser(
        section,
        field,
        cli_path,
        "|".join(re.escape(choice) for choice in choices),
    )


Pon_interfacesTemplate.PARSERS.extend(
    [
        _nested_value_parser("tc_layer_threshold", "error_frags_up", "tc-layer-threshold error-frags-up"),
        _nested_flag_parser("mcast_tc_layer", "mcast-tc-layer pm-collect", ("enable", "disable")),
        _nested_flag_parser("phy_layer", "phy-layer pm-collect", ("enable", "disable")),
        _nested_flag_parser("fec_tc_layer", "fec-tc-layer pm-collect", ("enable", "disable")),
        _nested_flag_parser("xg_tc_layer", "xg-tc-layer pm-collect", ("enable", "disable")),
        _nested_flag_parser("otdr", "otdr mode", ("enable", "disable", "test"), "mode"),
        _nested_flag_parser("utilization", "utilization pon-pmcollect", ("none", "pm-enable", "tca-enable", "inherit"), "pon_pmcollect"),
        _nested_flag_parser("utilization", "utilization ont-pmcollect", ("enable", "disable", "inherit"), "ont_pmcollect"),
        _nested_flag_parser("utilization", "utilization ontbulk-pmcollect", ("enable", "disable"), "ontbulk_pmcollect"),
        _nested_value_parser("deact_ont_tca", "mode", "deact-ont-tca mode"),
        _nested_value_parser("deact_ont_tca", "monitor_interval", "deact-ont-tca monitor-interval", r"\d+", "|int"),
    ]
)


for _field in (
    "txmcutilhi", "txmcutilmd", "txmcutillo", "txtotutilhi", "txtotutilmd",
    "txtotutillo", "rxtotutilhi", "rxtotutilmd", "rxtotutillo", "dbacongperiodhi",
    "dbacongperiodmd", "dbacongperiodlo", "txucdropfrmhi", "txucdropfrmmd",
    "txucdropfrmlo", "txmcdropfrmhi", "txmcdropfrmmd", "txmcdropfrmlo",
    "txbcdropfrmhi", "txbcdropfrmmd", "txbcdropfrmlo", "rxtotdropfrmhi",
    "rxtotdropfrmmd", "rxtotdropfrmlo", "numtcint", "numtcintdba", "dbacongthresh",
):
    Pon_interfacesTemplate.PARSERS.append(
        _nested_value_parser("utilization.threshold", _field, "utilization threshold %s" % _field)
    )


for _section, _prefix in (
    ("deact_ont_tca.threshold_percent", "deact-ont-tca threshold-percent"),
    ("deact_ont_tca.threshold_number", "deact-ont-tca threshold-number"),
):
    for _field in ("high", "high_clr", "low", "low_clr"):
        Pon_interfacesTemplate.PARSERS.append(
            _nested_value_parser(_section, _field, "%s %s" % (_prefix, _field), r"\d+", "|int")
        )
