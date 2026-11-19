# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
Grammar table for the isam_voice_sip resource (global SIP voice settings).

The device prints each node as one packed line ('info configure voice sip detail
flat', lab ISAM), e.g.::

    configure voice sip vsp vsp1 domain-name DomainName.com no admin-status no ta4 ...
    configure voice sip system session-timer no status no min-se-time no se-time no admin-status
    configure voice sip statistics stats-config per-line per-board no out-180-rsp ...

VOICE_SIP_NODES is the single description of that grammar, taken from the CLI guide:
the facts split and parse packed lines with it, the config class renders commands and
takes the device defaults from it, and the argspec and module documentation are generated
from it. An attribute is ``(option, cli, kind, default, choices, cli_node)``:

* kind ``flag``           -- on/off keyword (``[ [ no ] kw ]``); bool, default False.
* kind ``str``/``int``    -- value with a removal form (``[ no kw | kw <value> ]``).
* kind ``str-nono``/``int-nono`` -- value without a removal form (``[ kw <value> ]``).
* kind ``str-mand``/``int-mand`` -- mandatory value at creation (no removal form).
* ``default``             -- the device default; a value equal to it counts as unset
  (the device prints ``no kw``). ``None`` means no concrete default to compare.
* ``choices``             -- the guide's enumerated values, or None for a free value.
* ``cli_node``            -- overrides the node's CLI prefix (statistics has two nodes).

A node is ``(key, cli, identity, is_list, mandatory, attrs)``: ``identity`` is the option
holding the instance name (None for a flat section), ``is_list`` whether the config holds
a list of instances, ``mandatory`` the options required to create an instance.
"""

import re
import shlex

from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import remove_empties
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import parse_cli_fields

_PREFIX = "configure voice sip "

# (option, cli, kind, default, choices)
_LINEID = (
    ("syntax_pattern", "syntax-pattern", "str", "terminationuriordn",
     ["rpregisterdialog", "rpregister", "physicallineid", "terminationuriordn"]),
    ("pots_syntax", "pots-syntax", "str", None, None),
    ("isdn_syntax", "isdn-syntax", "str", None, None),
    ("cas_r2_syntax", "cas-r2-syntax", "str", None, None),
    ("cas_r1_syntax", "cas-r1-syntax", "str", None, None),
)

_VSP = (
    ("domain_name", "domain-name", "str-mand", None, None),
    ("admin_status", "admin-status", "str", "down", ["up", "down"]),
    ("tinfo", "tinfo", "int", 1000, None),
    ("ta4", "ta4", "int", 4000, None),
    ("ttir1", "ttir1", "int", 100, None),
    ("t_acm_delta", "t-acm-delta", "int", 18000, None),
    ("access_held_time", "access-held-time", "int", 600, None),
    ("awaiting_time", "awaiting-time", "int", 60, None),
    ("digit_send_mode", "digit-send-mode", "str", "en-bloc", ["en-bloc", "overlap-invite", "overlap-indialog"]),
    ("overlap_484_act", "overlap-484-act", "str", "release-call", ["release-call", "continue"]),
    ("dmpm_intdgt_expid", "dmpm-intdgt-expid", "str", "send-invite", ["send-invite", "release-call"]),
    ("dial_start_timer", "dial-start-timer", "int", 10, None),
    ("dial_long_timer", "dial-long-timer", "int", 20, None),
    ("dial_short_timer", "dial-short-timer", "int", 5, None),
    ("uri_type", "uri-type", "str", "sip-uri", ["sip-uri", "tel-uri", "sips-uri"]),
    ("rfc2833_pl_type", "rfc2833-pl-type", "int", 96, None),
    ("rfc2833_process", "rfc2833-process", "str", "audio", ["audio", "rfc2833", "both", "mandatory-audio"]),
    ("min_data_jitter", "min-data-jitter", "int", 50, None),
    ("init_data_jitter", "init-data-jitter", "int", 50, None),
    ("max_data_jitter", "max-data-jitter", "int", 50, None),
    ("release_mode", "release-mode", "str", "normal", ["normal", "caller", "callee", "both"]),
    ("dyn_pt_nego_type", "dyn-pt-nego-type", "str", "far-end", ["far-end", "asymmetric"]),
    ("vbd_g711a_pl_type", "vbd-g711a-pl-type", "int", 97, None),
    ("vbd_g711u_pl_type", "vbd-g711u-pl-type", "int", 98, None),
    ("vbd_mode", "vbd-mode", "str", "autoswitch", ["autoswitch", "renegotiation", "v152fb-autoswitch", "v152fb-reneg"]),
    ("warmline_dl_timer", "warmline-dl-timer", "int", 4, None),
    ("reg_sub", "reg-sub", "str", "disable", ["disable", "enable"]),
    ("dtmf_sip_info", "dtmf-sip-info", "str", "disable", ["disable", "enable"]),
    ("sub_period", "sub-period", "int", 3600, None),
    ("sub_head_start", "sub-head-start", "int", 600, None),
    ("t38_same_udp", "t38-same-udp", "str", "disable", ["disable", "enable"]),
    ("dhcp_option82", "dhcp-option82", "str", "disable", ["enable", "disable"]),
    ("sspprofile", "sspprofile", "str", None, None),
    ("signaling_ipmode", "signaling-ipmode", "str", "legacy-ipv4", ["legacy-ipv4", "ipv4", "ipv6"]),
    ("tls_cafile", "tls-cafile", "str", None, None),
    ("media_ipmode", "media-ipmode", "str", "legacy-ipv4", ["legacy-ipv4", "ipv4", "ipv6"]),
    ("timer_b", "timer-b", "int-nono", None, None),
    ("timer_f", "timer-f", "int-nono", None, None),
    ("timer_t1", "timer-t1", "int-nono", None, None),
    ("timer_t2", "timer-t2", "int-nono", None, None),
)

_REGISTER = (
    ("register_uri", "register-uri", "str", None, None),
    ("register_intv", "register-intv", "int", 3600, None),
    ("reg_retry_intv", "reg-retry-intv", "int", 60, None),
    ("reg_prev_ava_intv", "reg-prev-ava-intv", "int", 500, None),
    ("reg_head_start", "reg-head-start", "int", 600, None),
    ("reg_start_min", "reg-start-min", "int", 50, None),
    ("init_reg_delay", "init-reg-delay", "int", 180, None),
)

_REDUNDANCY = (
    ("support_redun", "support-redun", "str", "disable", ["enable", "disable"]),
    ("dns_purge_timer", "dns-purge-timer", "int", 86400, None),
    ("dns_ini_retr_int", "dns-ini-retr-int", "int", 500, None),
    ("dns_max_retr_nbr", "dns-max-retr-nbr", "int", 2, None),
    ("fg_monitor_method", "fg-monitor-method", "str", "register-method",
     ["register-method", "options-method", "passive-heartbeat"]),
    ("fg_monitor_int", "fg-monitor-int", "int", 90, None),
    ("bg_monitor_method", "bg-monitor-method", "str", "options-method", ["options-method"]),
    ("bg_monitor_int", "bg-monitor-int", "int", 3600, None),
    ("stable_obs_period", "stable-obs-period", "int", 21600, None),
    ("fo_hystersis", "fo-hystersis", "int", 0, None),
    ("del_upd_threshold", "del-upd-threshold", "int", 0, None),
    ("auto_server_fo", "auto-server-fo", "str", "disable", ["enable", "disable"]),
    ("auto_server_fb", "auto-server-fb", "int", 0, None),
    ("auto_sos_fo", "auto-sos-fo", "str", "disable", ["enable", "disable"]),
    ("auto_sos_fb", "auto-sos-fb", "int", 0, None),
    ("rtry_after_thrsh", "rtry-after-thrsh", "int", 0, None),
    ("options_max_fwd", "options-max-fwd", "int", 0, None),
    ("dns_redun_mode", "dns-redun-mode", "str", "dns-redun-primary", ["dns-redun-primary", "dns-redun-success"]),
    ("fail_obs_timer", "fail-obs-timer", "int", 240, None),
    ("fg_intv_503", "fg-intv-503", "int", 2, None),
    ("time_thrsh_503", "time-thrsh-503", "int", 0, None),
    ("nbr_thrsh_503", "nbr-thrsh-503", "int", 1, None),
    ("auto_srv_fo_timer", "auto-srv-fo-timer", "int", 86400, None),
)

_SYSTEM = (
    ("enable", "enable", "flag", False, None),
    ("status", "status", "str", "disable", ["enable", "disable", "enable-uas"]),
    ("min_se_time", "min-se-time", "int", 90, None),
    ("se_time", "se-time", "int", 1800, None),
    ("admin_status", "admin-status", "str", "down", ["up", "down"]),
)

_REDUNDANCY_CMD = (
    ("start_time", "start-time", "int", 0, None),
    ("end_time", "end-time", "int", 0, None),
    ("fail_x_type", "fail-x-type", "str-nono", None, ["geo-fail-over", "geo-fail-back"]),
)

# statistics spans two CLI nodes: the value attributes on 'statistics', the on/off
# response counters on 'statistics stats-config' (cli_node override per attribute).
_STATISTICS = (
    ("stats_5min_config", "stats-5min-config", "str", "disable", ["disable", "enable"], None),
    ("cdr_config", "cdr-config", "str", "disable", ["disable", "enable"], None),
    ("per_line", "per-line", "flag", False, None, "statistics stats-config"),
    ("per_board", "per-board", "flag", False, None, "statistics stats-config"),
    ("per_system", "per-system", "flag", False, None, "statistics stats-config"),
    ("per_call", "per-call", "flag", False, None, "statistics stats-config"),
    ("out_any_rsp", "out-any-rsp", "flag", False, None, "statistics stats-config"),
    ("out_180_rsp", "out-180-rsp", "flag", False, None, "statistics stats-config"),
    ("out_200_rsp", "out-200-rsp", "flag", False, None, "statistics stats-config"),
    ("in_any_rsp", "in-any-rsp", "flag", False, None, "statistics stats-config"),
    ("in_180_rsp", "in-180-rsp", "flag", False, None, "statistics stats-config"),
    ("in_200_rsp", "in-200-rsp", "flag", False, None, "statistics stats-config"),
)

_CAS_NSM = (
    ("version_nbr", "version-nbr", "int", 1, None),
    ("outg_from_no_cgpn", "outg-from-no-cgpn", "str", "impu-gdn", ["impu-gdn", "unavailable"]),
    ("international_prefix", "international-prefix", "str-mand", None, None),
    ("national_prefix", "national-prefix", "str", None, None),
    ("country_code", "country-code", "str-mand", None, None),
    ("outg_cpn_length", "outg-cpn-length", "int-mand", None, None),
)


def _node(key, cli, identity, is_list, mandatory, attrs):
    # normalise attrs to 6-tuples (option, cli, kind, default, choices, cli_node)
    norm = tuple(a if len(a) == 6 else a + (None,) for a in attrs)
    return {"key": key, "cli": cli, "identity": identity, "is_list": is_list,
            "mandatory": tuple(mandatory), "attrs": norm}


VOICE_SIP_NODES = (
    _node("lineid_syn_prof", "lineid-syn-prof", "name", True, (), _LINEID),
    _node("vsp", "vsp", "name", True, ("domain_name",), _VSP),
    _node("register", "register", "name", True, (), _REGISTER),
    _node("redundancy", "redundancy", "name", True, (), _REDUNDANCY),
    _node("system", "system session-timer", None, False, (), _SYSTEM),
    _node("redundancy_cmd", "redundancy-cmd", "name", True, (), _REDUNDANCY_CMD),
    _node("statistics", "statistics", None, False, (), _STATISTICS),
    _node("cas_nsm_prof", "cas-nsm-prof", "name", True,
          ("international_prefix", "country_code", "outg_cpn_length"), _CAS_NSM),
)

NODES_BY_KEY = dict((n["key"], n) for n in VOICE_SIP_NODES)
# longest CLI prefix first so 'statistics stats-config' wins over 'statistics'
_NODES_BY_CLI = sorted(VOICE_SIP_NODES, key=lambda n: -len(n["cli"]))

_VALUE_KINDS = ("str", "int", "str-mand", "int-mand", "str-nono", "int-nono")
_INT_KINDS = ("int", "int-mand", "int-nono")
_REMOVABLE_KINDS = ("str", "int", "flag")


def is_value(kind):
    return kind in _VALUE_KINDS


def is_int(kind):
    return kind in _INT_KINDS


def is_removable(kind):
    return kind in _REMOVABLE_KINDS


def cli_node(node, attr):
    return attr[5] or node["cli"]


def value_fields(node):
    """{cli: 'int'|'str'} of the node's value attributes (for parse_cli_fields)."""
    return dict((a[1], "int" if is_int(a[2]) else "str") for a in node["attrs"] if is_value(a[2]))


def flag_fields(node):
    return tuple(a[1] for a in node["attrs"] if a[2] == "flag")


def quote_value(value):
    """A value with whitespace, empty, or starting with '#' is sent in double quotes,
    as the device prints it (lab ISAM)."""
    text = str(value)
    if not text or text.startswith("#") or any(c.isspace() for c in text) or '"' in text:
        return '"%s"' % text.replace('"', '\\"')
    return text


def without_defaults(config):
    """A copy of config without values equal to their device default (defaults count as
    unset; the device prints them as 'no kw'). Mandatory values are always kept."""
    config = deepcopy(config or {})
    for node in VOICE_SIP_NODES:
        entries = config.get(node["key"])
        if node["is_list"]:
            entries = entries or []
        else:
            entries = [entries] if isinstance(entries, dict) else []
        for entry in entries:
            for option, _cli, kind, default, _choices, _sub in node["attrs"]:
                if default is not None and kind != "flag" and entry.get(option) == default:
                    del entry[option]
    return remove_empties(config)


def parse_lines(data):
    """Parse packed 'configure voice sip ...' lines into the resource config dict."""
    result = {}
    for raw in str(data or "").splitlines():
        line = raw.strip()
        if not line.startswith(_PREFIX):
            continue
        tokens = shlex.split(line[len(_PREFIX):])
        if not tokens:
            continue
        for node in _NODES_BY_CLI:
            cli_words = node["cli"].split()
            if tokens[:len(cli_words)] != cli_words:
                continue
            rest = tokens[len(cli_words):]
            name = None
            if node["identity"]:
                if not rest:
                    break
                name, rest = rest[0], rest[1:]
            fields = parse_cli_fields(rest, bool_fields=flag_fields(node),
                                      value_fields=value_fields(node), none_for_negated_values=True)
            if node["is_list"]:
                entry = dict(fields, name=name)
                bucket = result.setdefault(node["key"], {})
                bucket.setdefault(name, {"name": name}).update(entry)
            else:
                result.setdefault(node["key"], {}).update(fields)
            break
    for node in VOICE_SIP_NODES:
        if node["is_list"] and node["key"] in result:
            result[node["key"]] = list(result[node["key"]].values())
    return result


def render_attr(kind, cli, value):
    """Field tokens setting one attribute to value (value already given, not None)."""
    if kind == "flag":
        return [cli] if value else ["no", cli]
    if is_int(kind):
        return [cli, str(value)]
    return [cli, quote_value(value)]


def _target_tokens(kind, cli, value, default):
    """Setting to the device default is a reset (no kw) where a removal form exists."""
    if value == default and is_removable(kind):
        return ["no", cli]
    return render_attr(kind, cli, value)


def diff_tokens(node, want, have, state):
    """{cli_node: [field tokens]} of the attributes to send for one instance/section.

    merged sends only changed attributes; replaced/overridden also reset omitted
    removable attributes; rendered sends every given attribute (explicit False as no).
    want is raw (an explicit default means 'reset to default'); have holds non-defaults
    only, so a default equal to an absent have value is already in effect (no command).
    """
    groups = {}
    for option, cli, kind, default, _choices, _sub in node["attrs"]:
        w, h = want.get(option), have.get(option)
        tokens = None
        if state == "rendered":
            if w is not None:
                tokens = render_attr(kind, cli, w)
        elif state == "merged":
            if w is not None and w != h and not (w == default and h is None):
                tokens = _target_tokens(kind, cli, w, default)
        elif state in ("replaced", "overridden"):
            if w is None:
                if h is not None and is_removable(kind):
                    tokens = ["no", cli]
            elif w != h and not (w == default and h is None):
                tokens = _target_tokens(kind, cli, w, default)
        if tokens:
            groups.setdefault(cli_node(node, (option, cli, kind, default, _choices, _sub)), []).extend(tokens)
    return groups


def instance_command(node, name, tokens):
    parts = [_PREFIX.rstrip(), node["cli"]]
    if name is not None:
        parts.append(quote_value(name))
    return " ".join(parts + tokens)


def removal_command(node, name):
    return "%sno %s %s" % (_PREFIX, node["cli"], quote_value(name))


class Isam_voice_sipTemplate(NetworkTemplate):
    """Holds the grammar table; parsing and rendering are table-driven (see above)."""

    def __init__(self, lines=None, module=None):
        super(Isam_voice_sipTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    def parse(self):
        return parse_lines("\n".join(self._lines or []))

    PARSERS = []
